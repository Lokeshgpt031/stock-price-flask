import yfinance as yf
import os
import json
from constants import *

from flask import Flask, render_template

app = Flask(__name__)

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
def get_stock_history(name,period):
  ticker=yf.Ticker(name).history(period)
  ticker.reset_index(inplace=True)
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
