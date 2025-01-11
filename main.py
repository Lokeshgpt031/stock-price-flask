import yfinance as yf
import os
import json
from constants import *
from flask_cors import CORS

from flask import Flask, render_template

app = Flask(__name__)
CORS(app)

@app.route("/")
def hello_world():
    """Example Hello World route."""
    data = {
        "Get Stock Price": "/api/stockprice/<name>",
        "Get Stock History": "/api/history/<name>/<period>",
        "Get Earning History": "/api/earninghistory/<name>",
        "Get Ticker Info": "/api/info/<name>"
    }
    return render_template('table.html', data=data)

@app.route("/api/stockprice/<name>")
def get_stock_price(name):
    ticker = yf.Ticker(name).history_metadata
    datares = {}
    for i in metaData:
        try:  
            datares[i] = ticker[i]
        except:
            datares[i] = ''  # Set to empty string if key is not found
    return json.dumps(datares)

@app.route("/api/history/<name>/<period>")
def get_stock_history(name, period):
    if period == "1d":
        interval = "5m"
    elif period in ["5d", "1mo"]:
        interval = "15m"
    elif period in ["3mo", "6mo", "1y"]:
        interval = "1d"
    elif period in ["2y", "5y", "10y"]:
        interval = "1wk"
    else:
        interval = "1mo"

    ticker = yf.Ticker(name).history(period=period, interval=interval)
    ticker.reset_index(inplace=True)
    ticker.rename(columns={"index": "Date"}, inplace=True)
    # if column as Datetime change to Date
    if ticker.columns[0] == "Datetime":
        ticker["Date"] = ticker["Datetime"].dt.strftime("%Y-%m-%d %H:%M:%S")

    return ticker.to_json()


@app.route("/api/earninghistory/<name>")
def earning_history(name):
  ticker=yf.Ticker(name).earnings_history
  ticker.reset_index(inplace=True)
  ticker.rename(columns={"index": "Dates"},inplace=True)

  return (ticker.to_json())

@app.route("/api/info/<name>")
def get_ticker_info(name):
    ticker = yf.Ticker(name)
    info = ticker.info
    return json.dumps(info)

if __name__ == "__main__":
    app.run()
