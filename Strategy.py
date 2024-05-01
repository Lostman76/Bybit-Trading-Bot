import ta.momentum
import ta.trend
import ta.volume
from keys import api, secret, accountType
from pybit.unified_trading import HTTP
import pandas as pd
import ta 
import time
from Bybit import BybitClient

session  = BybitClient(api, secret, accountType)


tp = 0.012 # TP = 1.2%
sl = 0.09 # SL = -0.9%
timeframe = 15 # 30 minutes
mode = 1 # 1- isolated, 0-cross

leverage = 10
qty = float(session.get_balance())*0.2

def get_balance():
    balance = session.get_wallet_balance(accountType = "Contract", coin = "USDT")['result']['list'][0]['coin'][0]['walletBalance']
    balance = float(balance)
    print(f'Balance : {get_balance} USDT')


def Indicator_signal(symbol):
    kl = session.get_candles(symbol, timeframe)
    ema_20 = ta.trend.ema_indicator(kl.Close, window=20)
    ema_50 = ta.trend.ema_indicator(kl.Close, window=50)
    ema_200 = ta.trend.ema_indicator(kl.Close, window= 200)
    rsi = ta.momentum.RSIIndicator(kl.Close, window=14).rsi()
    vwap = ta.volume.volume_weighted_average_price(kl.High, kl.low, kl.Close, kl.Volume, window = 30)
    dif = abs
    # (abs(float(kl.Close.iloc[-1]) - float(ema_20.iloc[-1])) >= 0.04)
    # print(rsi)
    if (rsi.iloc[-1]<30) & (abs(float(kl.Close.iloc[-1]) - float(vwap.iloc[-1]))/(float(vwap.iloc[-1])) >=0.035):
        return 'up'
    elif (rsi.iloc[-1] >70) & (abs(float(kl.Close.iloc[-1]) - float(vwap.iloc[-1]))/(float(vwap.iloc[-1])) >=0.035):
        return 'down'
    else:
        return 'none'

# Rsi_signal(symbol = "INJUSDT")



def williamsR(symbol):
    kl =session.get_candles(symbol, timeframe)
    w = ta.momentum.WilliamsRIndicator(kl.High, kl.low, kl.Close, lbp=24).williams_r()
    ema_w = ta.trend.ema_indicator(w, window = 24)
    if w.iloc[-1]<-99.5:
        return 'up'
    elif w.iloc[-1]>-0.5:
        return 'down'
    elif w.iloc[-1]<-75 and w.iloc[-2]<-70 and w.iloc[-2] < ema_w.iloc[-2] and w.iloc[-1]> ema_w.iloc[-1]:
        return 'up'
    elif w.iloc[-1]>-25 and w.iloc[-2]>-30 and w.iloc[-2] > ema_w.iloc[-2] and w.iloc[-1]< ema_w.iloc[-1]:
        return 'down'
    else:
        return 'none'
    
max_pos = 50 

symbols = session.get_tickers()

while True:
    balance = session.get_balance()
    if balance ==None:
        print('Cant connect')
    if balance != None:
        balance = float(balance)
        print(f'Balance:{balance} USDT')
        pos = session.get_pos()
        print(f'you have {len(pos)} positoions:{pos}')

        if len(pos)<max_pos:
            for i in symbols:
                pos = session.get_pos()
                if len(pos)>=max_pos:
                    break

                signal = Indicator_signal(i)

                if signal =='up':
                    print(f'Found Buy signal for {i}')
                    session.set_mode(i)
                    time.sleep(2)
                    session.Place_order_mkt(i, 'buy')
                    time.sleep(5)

                if signal =='down':
                    print(f'Found Sell signal for {i}')
                    session.set_mode(i)
                    time.sleep(2)
                    session.Place_order_mkt(i, 'sell', mode=1, leverage=10, qty = qty)
                    time.sleep(5)
    print("waiting 2 mins")
    time.sleep(120)
    

