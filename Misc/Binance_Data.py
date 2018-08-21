import numpy as np
import pandas as pd
import Signals_Testing as signals
from binance.client import Client
from scipy.stats import linregress

class BinanceData:
    def __init__(self,SYMBOLS):
        #FILL IN API KEY
        API_KEY = ""
        API_SECRET = ""

        self.client = Client(API_KEY, API_SECRET)

        self.SYMBOLS = SYMBOLS

    def getDataArray(self, symbol, trait, frequency=Client.KLINE_INTERVAL_1HOUR, period='1 day ago UTC'):
        # symbols = string, trait must be numeric

        HEADER_COLUMNS = ["Open_Time", "Open", "High", "Low", "Close", "Volume", "Close_Time", "Quote_Asset_Volume",
                          "Num_Of_Trades", "Taker_Buy_Volume", "Taker_Buy_Quote_Volume", "Nothing"]

        coin1 = pd.DataFrame(self.client.get_historical_klines(symbol, frequency, period), columns=HEADER_COLUMNS)
        output = coin1[trait].values
        output = np.array(map(lambda x: float(x), output))
        return output

    #Returns array of Open and Closing Relative Prices vs ETH
    def getOpenCloseArrays(self, symbol,frequency=Client.KLINE_INTERVAL_1HOUR,period='1 day ago UTC'):
        #symbols = string

        HEADER_COLUMNS = ["Open_Time","Open","High","Low","Close","Volume","Close_Time","Quote_Asset_Volume","Num_Of_Trades","Taker_Buy_Volume","Taker_Buy_Quote_Volume","Nothing"]

        coin1 = pd.DataFrame(self.client.get_historical_klines(symbol, frequency, period),columns=HEADER_COLUMNS)
        open = coin1['Open'].values
        open = np.array(map(lambda x: float(x), open))
        close = coin1['Close'].values
        close = np.array(map(lambda x: float(x), close))

        #return array, array
        return open, close

    def getOpenCloseArraysAbsolute(self, symbol,frequency=Client.KLINE_INTERVAL_1HOUR,period='1 day ago UTC'):
        # symbols = string

        HEADER_COLUMNS = ["Open_Time", "Open", "High", "Low", "Close", "Volume", "Close_Time", "Quote_Asset_Volume",
                          "Num_Of_Trades", "Taker_Buy_Volume", "Taker_Buy_Quote_Volume", "Nothing"]

        coin1 = pd.DataFrame(self.client.get_historical_klines(symbol, frequency, period), columns=HEADER_COLUMNS)
        open = coin1['Open'].values
        open = np.array(map(lambda x: float(x), open))
        close = coin1['Close'].values
        close = np.array(map(lambda x: float(x), close))
        abs_open = open
        abs_close = close
        if symbol != "ETHUSDT":
            eth = pd.DataFrame(self.client.get_historical_klines("ETHUSDT", frequency, period), columns=HEADER_COLUMNS)
            e_open = eth['Open'].values
            e_open = np.array(map(lambda x: float(x), e_open))
            e_close = eth['Close'].values
            e_close = np.array(map(lambda x: float(x), e_close))

            abs_open =  open * e_open
            abs_close = close * e_close

        # return array, array
        return abs_open, abs_close

    #@WORK IN PROGRESS
    def getOpenCloseArraysAbsoluteMulti(self,symbols,frequency=Client.KLINE_INTERVAL_1HOUR,period='1 day ago UTC'):
        # symbols = list
        out = pd.DataFrame()
        for symbol in symbols:
            if symbol != 'ETHUSDT':
                out[symbol] = getOpenCloseArraysAbsolute(symbol, frequency, period)
            else:
                out[symbol] = getOpenCloseArrays(symbol, frequency, period)
        #return DataFrame[date, symbols1, symbol2...]
        return out

    #Returns array of Open and Closing Absolute Prices
    def getPctChangeArray(self,symbol,getOpenCloseArrays=getOpenCloseArrays):
        #symbol = string
        open, close = getOpenCloseArrays(symbol)
        change = (open - close) / open

        #return array
        return change

    def getPctChgMulti(self,symbols):
        #symbols = list
        out =  pd.DataFrame()
        for symbol in symbols:
            out[symbol] = getPctChangeArray(symbol,getOpenCloseArrays=getOpenCloseArrays)

        #return DataFrame[date, symbols1, symbol2...]
        return out

    #Returns array of Percentage Return
    def getTotalReturn(self,symbol,getOpenCloseArrays=getOpenCloseArrays,frequency=Client.KLINE_INTERVAL_1HOUR,period='1 day ago UTC'):
        #symbol = string
        #Use getOpenCloseArrays for Relative Return vs ETH or getOpenCloseArraysAbsolute for Absolute Return

        open, close = getOpenCloseArrays(symbol,frequency,period)
        return (close[close.size-1] - close[0])/1.0/close[0]

    def getTotalReturnsMulti(self,symbols,getOpenCloseArrays=getOpenCloseArrays,frequency=Client.KLINE_INTERVAL_1HOUR,period='1 day ago UTC'):
        #symbol = list
        out = []
        for symbol in symbols:
            out.append(self.getTotalReturn(symbol,getOpenCloseArrays=getOpenCloseArrays,frequency=frequency,period=period))
        out = pd.DataFrame(out,index=symbols,columns=['Returns'])
        out.sort_values(by=['Returns'],inplace=True)
        return out

    def getCorrelationWithETH(self,symbol,getOpenCloseArrays=getOpenCloseArrays):
        #symbol = string
        eth_open, eth_close = getOpenCloseArrays('ETHUSDT')
        open, close = getOpenCloseArrays(symbol)
        eth_chg =  (eth_open - eth_close)/eth_open
        chg = (open - close)/open
        return np.corrcoef(chg, eth_chg)[0][1]

    def getCorrelationWithEthMulti(self,symbols,getOpenCloseArrays=getOpenCloseArrays):
        #symbols = list
        out = []
        for symbol in symbols:
            out.append(self.getCorrelationWithETH(symbol,getOpenCloseArrays=getOpenCloseArrays))
        out = pd.DataFrame(out, index=symbols, columns=['Correlations'])
        out.sort_values(by=['Correlations'],inplace=True)
        return out

    #@WORK IN PROGRESS
    def getVolumeArray(self,symbol,frequency=Client.KLINE_INTERVAL_1HOUR,period='1 day ago UTC'):
        #symbol = string
        HEADER_COLUMNS = ["Open_Time", "Open", "High", "Low", "Close", "Volume", "Close_Time", "Quote_Asset_Volume",
                          "Num_Of_Trades", "Taker_Buy_Volume", "Taker_Buy_Quote_Volume", "Nothing"]

        coin1 = pd.DataFrame(self.client.get_historical_klines(symbol, frequency, period), columns=HEADER_COLUMNS)
        volume = coin1['Volume'].values
        volume = np.array(map(lambda x: float(x), open))

        # return array
        return volume

    #@WORK IN PROGRESS
    def getRollingReturns(self,symbols,frequency=Client.KLINE_INTERVAL_1HOUR,period='1 day ago UTC'):
        eth_open,eth_close = self.getOpenCloseArrays('ETHUSDT', frequency, period )

        coin_open, coin_close = self.getOpenCloseArraysAbsolute(symbols, frequency, period)

        out = pd.DataFrame()
        out['ETHUSDT'] = eth_open
        out[symbols] = coin_open
        print(out)
        return out

    #Return a beta between two coins
    def getBeta(self, symbol1, symbol2,frequency=Client.KLINE_INTERVAL_1HOUR,period='1 day ago UTC'):
        o1,p1 = self.getOpenCloseArraysAbsolute(symbol1,frequency,period)
        o2, p2 = self.getOpenCloseArraysAbsolute(symbol2, frequency, period)
        slope, intercept, rval, pval, stderr, = linregress(p1,p2)

        return slope


SYMBOLS = ['ETHUSDT','VENETH','KNCETH','REQETH','SUBETH','QTUMETH',
                   'ICXETH','OMGETH','XRPETH','NEOETH','ADAETH','WTCETH',
                   'XLMETH','IOTAETH','EOSETH','DASHETH','TRXETH','XMRETH',
                   'LRCETH','STRATETH','ZRXETH','BNBETH','ARKETH']

binance = BinanceData(SYMBOLS)

totalReturns = binance.getTotalReturnsMulti(binance.SYMBOLS,getOpenCloseArrays=binance.getOpenCloseArraysAbsolute,frequency=Client.KLINE_INTERVAL_1HOUR,period='3 day ago UTC')

totalReturnsVsETH = binance.getTotalReturnsMulti(binance.SYMBOLS,getOpenCloseArrays=binance.getOpenCloseArrays,frequency=Client.KLINE_INTERVAL_1HOUR,period='3 day ago UTC')
totalReturnsVsETH = totalReturnsVsETH.rename(columns={"Returns":"ReturnsVsEth"})

correlations = binance.getCorrelationWithEthMulti(binance.SYMBOLS,getOpenCloseArrays=binance.getOpenCloseArraysAbsolute)

#print(binance.getBeta('ETHUSDT','VENETH',Client.KLINE_INTERVAL_1HOUR,period='1 day ago UTC'))

result = pd.concat([totalReturns,totalReturnsVsETH, correlations], axis=1, join='outer')

result.sort_values(by=['Returns'], inplace=True)

print(result)






PATH = 'C:/Users/Frank Zhi/Desktop/Crypto_Analysis.xlsx'
TAB = 'VEN'
#data = getRollingReturns('VENETH',frequency=Client.KLINE_INTERVAL_30MINUTE,period='20 day ago UTC')
#signals.write(data,PATH,TAB)


'''
# fetch 30 minute klines for the last month of 2017
klines = client.get_historical_klines("ETHBTC", Client.KLINE_INTERVAL_30MINUTE, "1 Dec, 2017", "1 Jan, 2018")

# fetch weekly klines since it listed
klines = client.get_historical_klines("VENETH", Client.KLINE_INTERVAL_1HOUR, "12 Jan, 2018")

prices =  client.get_all_tickers()
'''