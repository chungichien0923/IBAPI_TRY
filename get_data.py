from ibapi.client import EClient
from ibapi.wrapper import EWrapper
from ibapi.contract import Contract

import threading
import time

import pandas as pd
import pandas_datareader.data as web

##################################################################################################################################################################################################

with open('/Users/chungichien/Desktop/資產配置/trade/alpha_vantage_key/Key_chungichien0923.txt') as key_file:
    alpha_vantage_key = key_file.read()

#########################################################################
class IBapi(EWrapper, EClient):
    def __init__(self):
        # 使用 父類別.__init__(self, ...) 將會在此子類別中設定父類別中初始化的屬性
        # EWrapper.__init__(self)
        EClient.__init__(self, self)
        self.data = [] #Initialize variable to store candle
    def historicalData(self, reqId, bar):
        # print(f'Time: {bar.date} Open: {bar.open} High: {bar.high} Low: {bar.low} Close: {bar.close}')
        self.data.append([bar.date, bar.open, bar.high, bar.low, bar.close])


def IB_data(from_symbol: str='EUR', to_symbol: str='USD', endDateTime: str='', durationStr: str='10 Y', barSizeSetting: str='1 day', whatToShow: str='MIDPOINT', useRTH: int=0):
    """從 Interactive Broker 獲得資料，發生以下情形會被 Ban 掉: 1. 在 15 秒內發出相同的歷史數據請求. 2. 在兩秒內對同一合約、交易所和報價類型發出六個或更多歷史數據請求. 3. 在任何十分鐘內發出超過 60 個請求.

    Args:
        from_symbol (str, optional): Defaults to 'EUR'.
        
        to_symbol (str, optional): Defaults to 'USD'.
        
        endDateTime (str, optional): yyyymmdd HH:mm:ss ttt, where "ttt" is the optional time zone. Defaults to ''.
        
        durationStr (str, optional): 數字、空格、大寫字母，如: S (seconds), D (days) or W (week). If no unit is specified, seconds is used. Defaults to '10 Y'.
        
        barSizeSetting (str, optional): 1 sec, 5 secs, 15 secs, 30 secs, 1 min, 2 mins, 3 mins, 5 mins, 15 mins, 30 mins, 1 hour, 1 day. Defaults to '1 day'.
        
        whatToShow (str, optional): TRADES, MIDPOINT, BID, ASK, BID_ASK, HISTORICAL_VOLATILITY, OPTION_IMPLIED_VOLATILITY. Defaults to 'MIDPOINT'.
        
        useRTH (int, optional): 0 - 回傳所有數據（包含非常規交易時間）. 1 - 僅回傳常規交易時間之數據. Defaults to 0.
    
    Returns:
        df: OHLC DataFrame with DateTime index
    """
    def run_loop():
        app.run()
    
    app = IBapi()
    app.connect('127.0.0.1', 7497, 1)

    #Start the socket in a thread
    api_thread = threading.Thread(target=run_loop, daemon=True)
    api_thread.start()

    time.sleep(1) #Sleep interval to allow time for connection to server

    #Create contract object
    currency_contract = Contract()
    currency_contract.symbol = from_symbol
    currency_contract.secType = 'CASH'
    currency_contract.exchange = 'IDEALPRO'
    currency_contract.currency = to_symbol

    # #Request historical candles
    app.reqHistoricalData(reqId=1,
                          contract=currency_contract,
                          endDateTime=endDateTime,
                          durationStr=durationStr,
                          barSizeSetting=barSizeSetting,
                          whatToShow=whatToShow,
                          useRTH=useRTH,
                          formatDate=1,
                          keepUpToDate=False,
                          chartOptions=[])

    time.sleep(5) #sleep to allow enough time for data to be returned

    #Working with Pandas DataFrames
    df = pd.DataFrame(app.data, columns=['DateTime', 'Open', 'High', 'Low', 'Close'])
    df['DateTime'] = pd.to_datetime(df['DateTime'])
    df = df.set_index('DateTime')

    app.disconnect()
    
    return df#.info()

#########################################################################
def YF_data(from_symbol: str='EUR', to_symbol: str='USD', start: str='2012-07-27', end: str='2022-07-26'):
    """從 Yahoo Finance 獲得資料

    Args:
        from_symbol (str, optional): Defaults to 'EUR'.
        
        to_symbol (str, optional): Defaults to 'USD'.
        
        start (str, optional): Defaults to '2012-07-27'.
        
        end (str, optional): Defaults to '2022-07-26'.

    Returns:
        df: OHLC DataFrame with DateTime index
    """
    if from_symbol == 'USD':
        symbol = to_symbol + '=X'
    else:
        symbol = from_symbol + to_symbol + '=X'
    df = web.DataReader(symbol, 'yahoo', start=start, end=end)
    df = df[['Open', 'High', 'Low', 'Close']]
    df.rename_axis('DateTime', inplace=True)
    return df#.info()

#########################################################################
def AV_data(from_symbol: str='EUR', to_symbol: str='USD', start: str='2012-07-27', end: str='2022-07-26'):
    """從 Alpha Vantage 獲得資料

    Args:
        from_symbol (str, optional): Defaults to 'EUR'.
        
        to_symbol (str, optional): Defaults to 'USD'.
        
        start (str, optional): Defaults to '2012-07-27'.
        
        end (str, optional): Defaults to '2022-07-26'.

    Returns:
        df: OHLC DataFrame with DateTime index
    """
    symbol = from_symbol + '/' + to_symbol
    df = web.DataReader(symbol, 'av-forex-daily', start=start, end=end, api_key=alpha_vantage_key)
    df.columns = ['Open', 'High', 'Low', 'Close']
    df.index = pd.to_datetime(df.index)
    df.rename_axis('DateTime', inplace=True)
    return df#.info()

# print(IB_data('EUR', 'USD', endDateTime='20220726 23:59:59'))
# print(YF_data('EUR', 'USD', start='2012-07-30', end='2022-07-26'))
# print(AV_data('EUR', 'USD', start='2012-07-30', end='2022-07-26'))