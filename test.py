import yfinance as yf
import json

dataGranularity= '1h'
range='5d'
validRanges= ['1d', '5d', '1mo', '3mo', '6mo', '1y', '2y', '5y', '10y', 'ytd', 'max']

msft = yf.Ticker("INFY.NS")

from yfinance.ticker import Ticker

# get all stock info
meta=Ticker("INFY.NS").get_history_metadata()
print(meta)

metaData=['currency',
 'symbol',
 'exchangeName',
 'fullExchangeName',
 'instrumentType',
 'firstTradeDate',
 'regularMarketTime',
 'hasPrePostMarketData',
 'gmtoffset',
 'timezone',
 'exchangeTimezoneName',
 'regularMarketPrice',
 'fiftyTwoWeekHigh',
 'fiftyTwoWeekLow',
 'regularMarketDayHigh',
 'regularMarketDayLow',
 'regularMarketVolume',
 'longName',
 'shortName',
 'chartPreviousClose',
 'previousClose',
 'scale',
 'priceHint',
 'currentTradingPeriod',
#  'tradingPeriods',
 'dataGranularity',
 'range',
 'validRanges']

# datares={}
# for i in metaData:
#     datares[i]=meta[i]
# print( json.dumps(datares,indent=4))
