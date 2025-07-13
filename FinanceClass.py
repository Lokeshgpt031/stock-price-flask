from datetime import datetime
import yfinance as yf
from constants import metaData
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed

class FinanceClass:
    """A utility class for fetching stock data using Yahoo Finance."""

    @staticmethod
    def get_stock_price(symbols):
        """Fetch stock metadata for given symbols (list or str) using ThreadPoolExecutor for faster response."""


        if isinstance(symbols, str):
            symbols = [symbols]
        results = [{} for _ in symbols]

        def fetch_metadata(idx, symbol):
            try:
                metadata = yf.Ticker(symbol).history_metadata
                results[idx] = {k: metadata.get(k, "") for k in metaData}
            except Exception:
                results[idx] = {}

        with ThreadPoolExecutor(max_workers=8) as executor:
            futures = [
                executor.submit(fetch_metadata, idx, symbol)
                for idx, symbol in enumerate(symbols)
            ]
            for future in futures:
                future.result()

        return results if len(results) != 1 else results[0]


    @staticmethod
    def get_ticker_info(symbols):
        """Retrieve general information about stock tickers (list or str) using threading."""
        if isinstance(symbols, str):
            symbols = [symbols]

        def fetch_info(symbol):
            try:
                return symbol, yf.Ticker(symbol).info
            except Exception:
                return symbol, {}

        results = {}
        with ThreadPoolExecutor(max_workers=8) as executor:
            futures = {executor.submit(fetch_info, symbol): symbol for symbol in symbols}
            for future in as_completed(futures):
                symbol, info = future.result()
                results[symbol] = info if info else {}

        # Return single dict if one symbol, else dict of all
        return results[symbols[0]] if len(symbols) == 1 else results


    @staticmethod
    def get_stock_history(symbol, period="1mo"):
        """Retrieve historical stock data for a given period."""
        interval_map = {
            "1d": "5m", "5d": "15m", "1mo": "15m",
            "3mo": "1d", "6mo": "1d", "1y": "1d", "max": "1d", "ytd": "1d",
            "2y": "1wk", "5y": "1wk", "10y": "1wk"
        }
        interval = interval_map.get(period, "1mo")
        try:
            df = yf.Ticker(symbol).history(period=period, interval=interval)
            df.reset_index(inplace=True)
            if "Datetime" in df.columns:
                df["Date"] = df["Datetime"].dt.strftime("%Y-%m-%d %H:%M:%S")
            elif "Date" not in df.columns:
                df.rename(columns={"index": "Date"}, inplace=True)
            return df.to_dict(orient="records")
        except Exception:
            return []

    @staticmethod
    def get_earning_history(symbol):
        """Get company's earnings history."""
        try:
            df = yf.Ticker(symbol).earnings_history
            df.reset_index(inplace=True)
            df.rename(columns={"index": "Dates"}, inplace=True)
            return df.to_dict(orient="records")
        except Exception:
            return []

    @staticmethod
    def get_earning_report_quarterly(symbol):
        """Get quarterly income statement."""
        try:
            return yf.Ticker(symbol).quarterly_income_stmt.to_dict()
        except Exception:
            return {}

    @staticmethod
    def get_earning_report_annually(symbol):
        """Get annual income statement."""
        try:
            return yf.Ticker(symbol).income_stmt.to_dict()
        except Exception:
            return {}

# Example Usage:
# if __name__ == "__main__":
#     finance = FinanceClass()
#     print(finance.get_stock_price(["INFY.NS", "ITC.NS"]))
#     print("---------------")
#     print(finance.get_ticker_info(["INFY"]))
#     print("---------------")
#     print(finance.get_earning_history("INFY"))
#     print("---------------")
#     print(finance.get_earning_report_annually("INFY"))
