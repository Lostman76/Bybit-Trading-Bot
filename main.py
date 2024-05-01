from keys import accountType, secret, api
import time
import ta
from threading import Thread
from Bybit import BybitClient


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
kl = session.get_candles(symbol, timeframe)
# print(kl)

# print(session.get_balance())


vwap = ta.volume.volume_weighted_average_price(kl.High, kl.low, kl.Close, kl.Volume, window = 30 )
vwap = vwap.iloc[5]
print(vwap)



