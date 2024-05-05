from keys import accountType, secret, api
import time
import ta
from threading import Thread
from Bybit import BybitClient
# from Support_Resistance import check_candle_signal_plot

session  = BybitClient(api, secret, accountType)


timeframe = 15
sl = 0.015
tp = 0.02
max_positions =100
symbol = "INJUSDT"

qty = (session.get_balance())*0.4
# qty = round(qty, 1)
side = 'buy'

# print(qty)
leverage = 10
mode = 1
# order = session.Place_order(symbol, side, mode, leverage, qty, tp = 0.012, sl = 0.09)
# print(session.get_instruments_precision(symbol))
# qty = 
# kl = session.get_candles(symbol, timeframe)
# print(kl.iloc[-1])
# FR = ['fundingRate']
print( session.Open_interest(symbol) )


# print(session.get_balance())
# check_candle_signal_plot(-1, 4,4,50,df,0.02)

# vwap = ta.volume.volume_weighted_average_price(kl.High, kl.low, kl.Close, kl.Volume, window = 30 )
# vwap = vwap.iloc[5]

# print(vwap)
# symbol = ["BTCUSDT", "ETHUSDT", "SOLUSDT", "OPUSDT", "FETUSDT", "LINKUSDT"]
# wick_threshold = {}
# for i in symbol:
#     wick_threshold[i] = float(session.get_candles(i, timeframe)['Close'].iloc[-1]) * 0.1
# print(wick_threshold)


# for sym in symbol:
#     df = session.get_candles(sym, timeframe)
# print(df[-1])

    
# symbol = ["BTCUSDT", "ETHUSDT", "SOLUSDT", "OPUSDT", "FETUSDT", "LINKUSDT"]
# wick_threshold = {}
# limit={}
# proximity = {}
# for i in symbol:
#     wick_threshold[i] = float(session.get_candles(i, timeframe)['Close'].iloc[-1]) * 0.04
#     limit[i] = float(session.get_candles(i, timeframe)['Close'].iloc[-1]) * 0.02

# for sym in symbol:
#     print(limit[sym])


