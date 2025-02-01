from datetime import datetime
import yfinance as yf
from constants import metaData

class FinanceClass:

    @staticmethod
    def get_stock_price(names):
        """Fetch stock metadata using Yahoo Finance."""
        res=[]
        try:
            for stock in names:
                ticker = yf.Ticker(stock).history_metadata
                datares = {i: ticker.get(i, "") for i in metaData}
                res.append(datares) if datares else res.append({}) 
        except Exception:
                pass  # Skip if an exception occurs
        return res if len(res)>1 else res[0]

    @staticmethod
    def get_ticker_info(names: list):
        """Retrieve general information about stock tickers."""
        res = []
        for stock in names:
            try:
                ticker = yf.Ticker(stock)
                data = ticker.info
                res.append(data) if data else res.append({})
            except Exception:
                pass  # Skip if an exception occurs
        return res[0] if len(res) == 1 else res  # Return single dict if only one valid stock


    
    @staticmethod
    def get_stock_history(name: str, period: str = "1mo"):
        """Retrieve stock historical data for the given period."""
        interval_map = {
            "1d": "5m",
            "5d": "15m", "1mo": "15m",
            "3mo": "1d", "6mo": "1d", "1y": "1d", "max": "1d", "ytd": "1d",
            "2y": "1wk", "5y": "1wk", "10y": "1wk"
        }
        interval = interval_map.get(period, "1mo")

        ticker = yf.Ticker(name).history(period=period, interval=interval)
        ticker.reset_index(inplace=True)
        ticker.rename(columns={"index": "Date"}, inplace=True)
        if "Datetime" in ticker.columns:
            ticker["Date"] = ticker["Datetime"].dt.strftime("%Y-%m-%d %H:%M:%S")
        
        return ticker.to_dict(orient='records')

    @staticmethod
    def get_earning_history(name: str):
        """Get company's earnings history."""
        ticker = yf.Ticker(name).earnings_history
        ticker.reset_index(inplace=True)
        ticker.rename(columns={"index": "Dates"}, inplace=True)
        return ticker.to_dict(orient='records')

    
    @staticmethod
    def get_earning_report_quarterly(name:str):
        ticker=yf.Ticker(name)
        return ticker.quarterly_income_stmt.to_dict()
    
    @staticmethod
    def get_earning_report_annually(name:str):
        ticker=yf.Ticker(name)
        return ticker.income_stmt.to_dict()
    

# Example Usage:
# finance = FinanceClass()
# print(finance.get_ticker_info(["CAMS.NS",""]))
# print("---------------")
# print(finance.get_stock_history("INFY", "1y"))
# print("---------------")
# print(finance.get_ticker_info("INFY"))
# print("---------------")
# print(finance.get_earning_history("INFY"))
# print("---------------")
# print(finance.get_earning_report("INFY"))
