import pandas as pd 
import numpy as np
import ta
import time
from Bybit import BybitClient
from keys import api, secret, accountType
from tqdm import tqdm
import plotly.graph_objects as go 

session  = BybitClient(api, secret, accountType)

symbol = "BTCUSDT"
timeframe = 60
df = session.get_candles(symbol, timeframe)
# print(df)


wick_threshold = 1

def support(df, index, left, right):
    if(df.low.iloc[index-left:index].min() < df.low.iloc[index] or df.low.iloc[index+1:right+1].min()<df.low.iloc[index]):
        return 0
    candle_body = abs(df.Open.iloc[index]-df.Close.iloc[index])
    lower_wick = min(df.Open.iloc[index], df.Close.iloc[index]) - df.low.iloc[index]
    if (lower_wick>candle_body) and (lower_wick>wick_threshold):
        return 1
    
    return 0

def resistance(df,index, left, right):
    if (df.High.iloc[index-left:index].max() > df.High.iloc[index].max() or df.High.iloc[index+1:right+1].max()>df.High.iloc[index].max()):
        return 0
    candle_body = abs(df.Open.iloc[index]-df.Close.iloc[index])
    Upper_wick = df.High.iloc[index] - max(df.Open.iloc[index] , df.Close.iloc[index])

    if (Upper_wick > candle_body) and (Upper_wick > wick_threshold):
        return 1
    

def closeResistance(index, level, lim, df):
    if(len(level)==0):
        return 0
    c1 = abs(df.High.iloc[index] - min(level, key= lambda x:abs(x-df.High.iloc[index]))) <=lim
    c2 = abs(max(df.Open.iloc[index], df.Close.iloc[index]) - min(level, key = lambda x:abs(x-df.High.iloc[index])))<=lim
    c3 = min(df.Open.iloc[index], df.Close.iloc[index]) <min(level, key=lambda x:abs(x-df.High.iloc[index]))
    c4 = df.low.iloc[index]<min(level, key=lambda x:abs(x-df.High.iloc[index]))

    if (c1 or c2) and c3 and c4 :
        return min(level, key= lambda x:abs(x-df.High.iloc[index]))
    else:
        return 0
    
def closeSupport(index, level, lim, df):
    if(len(level)==0):
        return 0
    c1 = abs(df.low.iloc[index] - min(level, key= lambda x:abs(x-df.low.iloc[index]))) <=lim
    c2 = abs(min(df.Open.iloc[index], df.Close.iloc[index]) - min(level, key = lambda x:abs(x-df.low.iloc[index])))<=lim
    c3 = max(df.Open.iloc[index], df.Close.iloc[index]) > min(level, key=lambda x:abs(x-df.low.iloc[index]))
    c4 = df.High.iloc[index] > min(level, key=lambda x:abs(x-df.High.iloc[index]))

    if (c1 or c2) and c3 and c4 :
        return min(level, key= lambda x:abs(x-df.low.iloc[index]))
    else:
        return 0
        
def is_below_res(index, level_back_candles, level, df):
    return df.iloc[index - level_back_candles:index-1, df.columns.get_loc('High')].max() < level

def is_above_support(index, level_back_candles, level, df):
    return df.iloc[index - level_back_candles:index-1, df.columns.get_loc('low')].min() < level
    
def Candle_signal(index, left,right, backCandle, df):
    ss=[]
    rr = []
    for i in range(index-backCandle, index-right):
        if support(df,i, left, right):
            ss.append(df.low.iloc[i])
        if resistance(df,i, left,right):
            rr.append(df.High.iloc[i])
        
    ss.sort()
    for i in range(1,len(ss)):
        if i>=len(ss):
            break
        if abs(ss[i] - ss[i-1])<=300:
            ss.pop(i)
    rr.sort(reverse=True)
    for i in range(1, len(rr)):
        if i>=len(rr):
            break
        if abs(rr[i]-rr[i-1])<=300:
            rr.pop(i)

    rrss = rr+ss
    rrss.sort()
    for i in range(1,len(rrss)):
        if(i>=len(rrss)):
            break
        if abs(rrss[i]-rrss[i-1])<=300:
            rrss.pop(i)

    Cr = closeResistance(index, rrss, 100, df)
    Cs = closeSupport(index,rrss, 100, df)

    if (Cr and is_below_res(index, 16, Cr, df)):
        return 1
    elif(Cs and is_above_support(index, 16, Cs, df)):
        return 2
    else:
        return 0

left = 5
right = 6
backCandle = 300
signal = [0 for i in range(len(df))]
for row in tqdm(range(backCandle+left, len(df)- right)):
    signal[row] = Candle_signal(row, left, right, backCandle, df)

df["signal"] = signal



print(df[df['signal'] ==1].count())

df[ (df['signal']==1) | (df['signal']==2)]

# print(df)

def pointpos(x):
    if x.loc['signal'] ==1:
        return x.loc['High'] +1e-4
    elif x.loc['signal'] ==2:
        return x.loc['low'] - 1e-4
    else:
        return np.nan
    
df['pointpos'] = df.apply(lambda row:pointpos(row), axis = 1)

dfpl = df.iloc[100:300]

fig = go.Figure(data=[go.Candlestick(x=dfpl.index, open=dfpl['Open'], 
                                     high=dfpl['High'], low=dfpl['low'], close=dfpl['Close'])])

fig.update_layout(
    autosize=False,
    width=1000,
    height=800, 
    paper_bgcolor='black',
    plot_bgcolor='black')
fig.update_xaxes(gridcolor='black')
fig.update_yaxes(gridcolor='black')
fig.add_scatter(x=dfpl.index, y=dfpl['pointpos'], mode="markers",
                marker=dict(size=8, color="MediumPurple"),
                name="Signal")
fig.show()

def check_candle_signal_plot(index, left,right, backCandle, df, proximity):
    ss= []
    rr = []
    for i in range(index - backCandle, index - right):
        if support(df, i, left, right):
            ss.append(df.low.iloc[i])
        if resistance(df,i, left, right):
            rr.append(df.High.iloc[i])

    ss.sort()
    i = 0
    while i <len(ss)-1:
        if abs(ss[i] - ss[i+1]) <= proximity:
            del ss[i+1]
        else:
            i+=1

    rr.sort(reverse= True)
    i = 0
    while i< len(rr)-1:
        if(abs(rr[i]- rr[i+1])<= proximity):
            del rr[i]
        else:
            i+=1

    dfpk = df.iloc[index - backCandle - left: index +right +50]
    fig = go.Figure(data=[go.Candlestick(x=dfpl.index,
                open=dfpl['Open'],
                high=dfpl['High'],
                low=dfpl['low'],
                close=dfpl['Close'])])
    
    c=0
    while (1):
        if(c>len(ss)-1 ):
            break
        fig.add_shape(type='line', x0= index-backCandle-left, y0=ss[c],
                    x1= index,
                    y1=ss[c],
                    line=dict(color="MediumPurple",width=2), name="Support"
                    )
        c+=1

    c=0
    while (1):
        if(c>len(rr)-1 ):
            break
        fig.add_shape(type='line', x0=index-backCandle-left, y0=rr[c],
                    x1=index,
                    y1=rr[c],
                    line=dict(color="Red",width=2), name="Resistance"
                    )
        c+=1    
    
    fig.update_layout(
    autosize=False,
    width=1400,
    height=1000,)
    
    fig.show()

    cR = closeResistance(index, rr, 100, dfpk)
    cS = closeSupport(index, ss, 100, dfpk)
    #print(cR, is_below_resistance(l,6,cR, dfpl))
    if (cR and is_below_res(index,16,cR, dfpk) ):#and df.RSI[l]>65
        return 1
    elif(cS and is_above_support(index,16,cS,dfpk) ):#and df.RSI[l]<35
        return 2
    else:
        return 0

check_candle_signal_plot(331, 4,4,300,df,200)