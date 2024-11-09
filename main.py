
import yfinance as yf
import os
import json
from constants import *

from flask import Flask

app = Flask(__name__)

@app.route("/")
def hello_world():
  """Example Hello World route."""
  name = os.environ.get("NAME", "World")
  return f"Hello {name}!"

@app.route("/api/stockprice/<name>")
def get_stock_price(name):
  ticker = yf.Ticker("MSFT")
  res=ticker.history_metadata
  datares={}
  for i in metaData:
    datares[i]=res[i]
  return(json.dumps(datares))

@app.route("/api/history/<name>/<period>")
def get_stock_history(name,period):
  ticker=yf.Ticker(name).history(period)
  return ticker.to_json()


@app.route("/api/earninghistory/<name>")
def earning_history(name):
  ticker=yf.Ticker(name).earnings_history.reset_index()
  ticker.index.name="Dates"
  return (ticker.to_json())

if __name__ == "__main__":
  app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 3000)))