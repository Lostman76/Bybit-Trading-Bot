# Import necessary libraries
from tqdm import tqdm
import matplotlib.pyplot as plt
import pandas as pd 
import numpy as np
import ta
import time
from Bybit import BybitClient
from keys import api, secret, accountType
from tqdm import tqdm
import plotly.graph_objects as go 

session  = BybitClient(api, secret, accountType)

# Define parameters
timeframe = 15
symbol = ["BTCUSDT", "ETHUSDT", "SOLUSDT", "OPUSDT", "FETUSDT", "LINKUSDT", "MATICUSDT", "AXSUSDT", "AVAXUSDT", "RUNEUSDT", "FILUSDT"]
# symbol = session.get_tickers()
wick_threshold = {}
limit = {}
proximity = 0.5  # Adjust as needed
srlim = {}
# df = session.get_candles(sym, timeframe)   

# Calculate parameters
for sym in symbol:
    df = session.get_candles(sym, timeframe)
    # close_price = candles['Close'].iloc[-1]
    # wick_threshold[sym] = close_price * 0.04
    # limit[sym] = close_price * 0.02
    # srlim[sym] = close_price * 0.015


def support(df, index, left, right):
        if(df.low.iloc[index-left:index].min() < df.low.iloc[index] or df.low.iloc[index+1: index+right-5].min()<df.low.iloc[index]):
            return 0
        candle_body = abs(df.Open.iloc[index]-df.Close.iloc[index])
        lower_wick = min(df.Open.iloc[index], df.Close.iloc[index]) - df.low.iloc[index]
        if (lower_wick>candle_body) and (lower_wick>wick_threshold[sym]):
            return 1
        return 0
    # print(wick_threshold[sym])

def resistance(df,index, left, right):
        if (df.High.iloc[index-left:index].max() > df.High.iloc[index].max() or df.High.iloc[index+1: index+right-5].max()>df.High.iloc[index].max()):
            return 0
        candle_body = abs(df.Open.iloc[index]-df.Close.iloc[index])
        Upper_wick = df.High.iloc[index] - max(df.Open.iloc[index] , df.Close.iloc[index])

        if (Upper_wick > candle_body) and (Upper_wick > wick_threshold[sym]):
            return 1
    

def closeResistance(index, level, limit, df):
        right = 0
        if(len(level)==0):
            return 0
        c1 = abs(df.High.iloc[index+right] - min(level, key= lambda x:abs(x-df.High.iloc[index+right]))) <=limit[sym]
        c2 = abs(max(df.Open.iloc[index+right], df.Close.iloc[index+right]) - min(level, key = lambda x:abs(x-df.High.iloc[index+right])))<=limit[sym]
        c3 = min(df.Open.iloc[index+right], df.Close.iloc[index+right]) <min(level, key=lambda x:abs(x-df.High.iloc[index+right]))
        c4 = df.low.iloc[index+right]<min(level, key=lambda x:abs(x-df.High.iloc[index+right]))

        if (c1 or c2) and c3 and c4 :
            return min(level, key= lambda x:abs(x-df.High.iloc[index+right]))
        else:
            return 0
        
    # print(limit[sym])
    
def closeSupport(index, level, limit, df):
        right = 0
        if(len(level)==0):
            return 0
        c1 = abs(df.low.iloc[index+right] - min(level, key= lambda x:abs(x-df.low.iloc[index+right]))) <=limit[sym]
        c2 = abs(min(df.Open.iloc[index+right], df.Close.iloc[index+right]) - min(level, key = lambda x:abs(x-df.low.iloc[index+right])))<=limit[sym]
        c3 = max(df.Open.iloc[index+right], df.Close.iloc[index+right]) > min(level, key=lambda x:abs(x-df.low.iloc[index+right]))
        c4 = df.High.iloc[index+right] > min(level, key=lambda x:abs(x-df.High.iloc[index+right]))

        if (c1 or c2) and c3 and c4 :
            return min(level, key= lambda x:abs(x-df.low.iloc[index+right]))
        else:
            return 0
        
def is_below_res(index, level_back_candles, level, df):#levelback candles no of candles we would like to test this condition on like 5 candles befor our current candle should be less or more than res or supp resp.
        return df.iloc[index - level_back_candles:index-1, df.columns.get_loc('High')].max() < level

def is_above_support(index, level_back_candles, level, df):
        return df.iloc[index - level_back_candles:index-1, df.columns.get_loc('low')].min() < level
    
# Define signal detection function
def Candle_signal(index, left, right, backCandle, df):
    ss = []
    rr = []
    for i in range(index-backCandle, index-right+6):
        if support(df, i, left, right):
            ss.append(df.low.iloc[i])
        if resistance(df, i, left, right):
            rr.append(df.High.iloc[i])

    ss.sort()
    for i in range(1, len(ss)):
        if i >= len(ss):
            break
        if abs(ss[i] - ss[i - 1]) <= srlim[sym]:
            ss.pop(i)
    rr.sort(reverse=True)
    for i in range(1, len(rr)):
        if i >= len(rr):
            break
        if abs(rr[i] - rr[i - 1]) <= srlim[sym]:
            rr.pop(i)

    rrss = rr + ss
    rrss.sort()
    for i in range(1, len(rrss)):
        if i >= len(rrss):
            break
        if abs(rrss[i] - rrss[i - 1]) <= srlim[sym]:
            rrss.pop(i)

    Cr = closeResistance(index, rrss, limit, df)
    Cs = closeSupport(index, rrss, limit, df)

    if Cr and is_below_res(index, 6, Cr, df):
        return 1
    elif Cs and is_above_support(index, 6, Cs, df):
        return 2
    else:
        return 0
    


# def pointpos(x):
#         if x.loc['signal'] ==1:
#             return x.loc['High'] +1e-4
#         elif x.loc['signal'] ==2:
#             return x.loc['low'] - 1e-4
#         else:
#             return np.nan
# df['pointpos'] = df.apply(lambda row:pointpos(row), axis = 1)

# dfpl = df.iloc[100:300]

# fig = go.Figure(data=[go.Candlestick(x=df.index, open=df['Open'], 
#                                      high=df['High'], low=df['low'], close=df['Close'])])

# fig.update_layout(
#     autosize=False,
#     width=1700,
#     height=1000, 
#     paper_bgcolor='black',
#     plot_bgcolor='black')
# fig.update_xaxes(gridcolor='black')
# fig.update_yaxes(gridcolor='black')
# fig.add_scatter(x=dfpl.index, y=df['pointpos'], mode="markers",
#                 marker=dict(size=8, color="MediumPurple"),
#                 name="Signal")
# fig.show()



# Main loop for signal detection
for sym in symbol:
    df = session.get_candles(sym, timeframe)
    # print("Calculating for symbol:", sym)
    wick_threshold[sym] = float(df['Close'].iloc[-1]) * 0.002
    limit[sym] = float(df['Close'].iloc[-1]) * 0.004
    srlim[sym] = float(df['Close'].iloc[-1]) * 0.029
    left = 5
    right = 6
    backCandle = 10
    signal = [0] * len(df)
    for row in tqdm(range(backCandle+left, len(df))):
        signal[row] = Candle_signal(row, left, right, backCandle, df)

    df["signal"] = signal
    # print(df)

    print(df[df['signal'] == 1].count())
    print(df[df['signal'] == 2].count())

    # Plot signals
    # plt.figure(figsize=(10, 6))
    # plt.plot(df.index, df['Close'], label='Close Price')
    # plt.scatter(df[df['signal'] == 1].index, df[df['signal'] == 1]['Close'], color='red', marker='^', label='Support Signal')
    # plt.scatter(df[df['signal'] == 2].index, df[df['signal'] == 2]['Close'], color='green', marker='v', label='Resistance Signal')
    # plt.title(f'Signals for {sym}')
    # plt.xlabel('Date')
    # plt.ylabel('Price')
    # plt.legend()
    # plt.show()
    def pointpos(x):
        if x.loc['signal'] ==1:
            return x.loc['High'] +1e-10
        elif x.loc['signal'] ==2:
            return x.loc['low'] - 1e-10
        else:
            return np.nan
    
    df['pointpos'] = df.apply(lambda row:pointpos(row), axis = 1)

    # fig = go.Figure(data=[go.Candlestick(x=df.index, open=df['Open'], 
    #                                  high=df['High'], low=df['low'], close=df['Close'])])

    # fig.update_layout(
    # autosize=False,
    # width=1700,
    # height=1000, 
    # paper_bgcolor='black',
    # plot_bgcolor='black')
    # fig.update_xaxes(gridcolor='black')
    # fig.update_yaxes(gridcolor='black')
    # fig.add_scatter(x=df.index, y=df['pointpos'], mode="markers",
    #             marker=dict(size=8, color="MediumPurple"),
    #             name="Signal")
    # fig.show()

    # time.sleep(50000)
    def check_candle_signal_plot(index, left,right, backCandle, df, srlim):
        ss= []
        rr = []
        for i in range(index - backCandle, index+6 ):
            if support(df, i, left, right):
                ss.append(df.low.iloc[i])
            if resistance(df,i, left, right):
                rr.append(df.High.iloc[i])

        ss.sort()
        i = 0
        while i <len(ss)-1:
            if abs(ss[i] - ss[i+1]) <= srlim[sym]:
                del ss[i+1]
            else:
                    i+=1

        rr.sort(reverse= True)
        i = 0
        while i< len(rr)-1:
            if(abs(rr[i]- rr[i+1])<= srlim[sym]):
                del rr[i]
            else:
                i+=1

        # dfpk = df.iloc[index - backCandle - left: index +right +50]
        # fig = go.Figure(data=[go.Candlestick(x=df.index,
        #             open=df['Open'],
        #             high=df['High'],
        #             low=df['low'],
        #             close=df['Close'])])
    
        c=0
        while (1):
            if(c>len(ss)-1 ):
                break
            # fig.add_shape(type='line', x0= index-backCandle-left, y0=ss[c],
            #         x1= index+6,
            #         y1=ss[c],
            #         line=dict(color="MediumPurple",width=2), name="Support"
            #         )
            c+=1

        c=0
        while (1):
            if(c>len(rr)-1 ):
                break
            # fig.add_shape(type='line', x0=index-backCandle-left, y0=rr[c],
            #         x1=index+6,
            #         y1=rr[c],
            #         line=dict(color="Red",width=2), name="Resistance"
            #         )
            c+=1    
    
        # fig.update_layout(
        # autosize=False,
        # width=1600,
        # height=1000)
    
        # fig.show()

        cR = closeResistance(index, rr, limit, df)
        cS = closeSupport(index, ss, limit, df)
    #print(cR, is_below_resistance(l,6,cR, dfpl))
        if (cR and is_below_res(index,6,cR, df) ):#and df.RSI[l]>65
            return 1
        elif(cS and is_above_support(index,6,cS,df) ):#and df.RSI[l]<35
            return 2
        else:
            return 0
    # check_candle_signal_plot(993, 5,6, 950,df, srlim)



