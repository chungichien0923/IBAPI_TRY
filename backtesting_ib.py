from ibapi.client import EClient
from ibapi.wrapper import EWrapper
from ibapi.contract import Contract

import threading
import time

import pandas as pd


# Taking data from IB
class IBapi(EWrapper, EClient):
    def __init__(self):
        # 使用 父類別.__init__(self, ...) 將會在此子類別中設定父類別中初始化的屬性
        # EWrapper.__init__(self)
        EClient.__init__(self, self)
        self.data = [] #Initialize variable to store candle
    def historicalData(self, reqId, bar):
        print(f'Time: {bar.date} Open: {bar.open} High: {bar.high} Low: {bar.low} Close: {bar.close}')
        self.data.append([bar.date, bar.open, bar.high, bar.low, bar.close])
		
def run_loop():
    app.run()

app = IBapi()
app.connect('127.0.0.1', 7497, 1)

#Start the socket in a thread
api_thread = threading.Thread(target=run_loop, daemon=True)
api_thread.start()

time.sleep(1) #Sleep interval to allow time for connection to server

#Create contract object
eurusd_contract = Contract()
eurusd_contract.symbol = 'EUR'
eurusd_contract.secType = 'CASH'
eurusd_contract.exchange = 'IDEALPRO'
eurusd_contract.currency = 'USD'


# # #Request historical candles
# app.reqHistoricalData(1, eurusd_contract, '', '6 M', '1 hour', 'BID', 0, 2, False, [])

# time.sleep(5) #sleep to allow enough time for data to be returned

# #Working with Pandas DataFrames
# df = pd.DataFrame(app.data, columns=['DateTime', 'Open', 'High', 'Low', 'Close'])
# df['DateTime'] = pd.to_datetime(df['DateTime'],unit='s',utc=True)

# print(df.index)


# #Request historical candles
app.reqHistoricalData(1, eurusd_contract, '', '6 M', '1 hour', 'BID', 0, 1, False, [])

time.sleep(5) #sleep to allow enough time for data to be returned

#Working with Pandas DataFrames
df = pd.DataFrame(app.data, columns=['DateTime', 'Open', 'High', 'Low', 'Close'])
df['DateTime'] = pd.to_datetime(df['DateTime'])
df = df.set_index('DateTime')

print(df)

app.disconnect()


# # Starting with data from yahoo finance
# import pandas_datareader.data as web

# df = web.DataReader('EURUSD=X', 'yahoo', start='2019-09-10')

# Create SMA calculation
def SMA(values, n):
    """
    Return simple moving average of `values`, at
    each step taking into account `n` previous values.
    """
    return pd.Series(values).rolling(n).mean()

# Override the Strategy class
from backtesting import Strategy
from backtesting.lib import crossover


class SmaCross(Strategy):
    # Define the two MA lags as *class variables*
    # for later optimization
    n1 = 10
    n2 = 20
    
    def init(self):
        # Precompute the two moving averages
        self.sma1 = self.I(SMA, self.data.Close, self.n1)
        self.sma2 = self.I(SMA, self.data.Close, self.n2)
    
    def next(self):
        # If sma1 crosses above sma2, close any existing
        # short trades, and buy the asset
        if crossover(self.sma1, self.sma2):
            # self.position.close()
            self.buy()

        # Else, if sma1 crosses below sma2, close any existing
        # long trades, and sell the asset
        elif crossover(self.sma2, self.sma1):
            # self.position.close()
            self.sell()

# Run Backtest
from backtesting import Backtest

bt = Backtest(df, SmaCross, margin=0.25, commission=0.002, exclusive_orders=True)
stats = bt.run()
# stats = bt.optimize(n1=range(5, 30, 5),
#                     n2=range(10, 70, 5),
#                     maximize='Equity Final [$]',
#                     constraint=lambda param: param.n1 < param.n2,
#                     method='grid')
# print(stats)
# print(stats['_trades'])
bt.plot(filename='./plots/sma.html')