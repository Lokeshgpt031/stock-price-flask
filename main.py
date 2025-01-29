import yfinance as yf
from markupsafe import Markup
import os
import json
from constants import *
from flask_cors import CORS
from Stocklist import *
from flask import Flask, render_template

app = Flask(__name__)
CORS(app)

@app.route("/")
def hello_world():
    """Example Hello World route."""
    data = {
        "Get Stock Price": Markup(f"<a href=\"/api/stockprice/<name>\">/api/stockprice/<name></a>"), # get stock price of a ticker
        "Get Stock History": Markup(f"<a href=\"/api/history/<name>/<period>\">/api/history/<name>/<period></a>"), #get stock price history in define period
        "Get Earning History": Markup(f"<a href=\"/api/earninghistory/<name>\">/api/earninghistory/<name></a>"), #get the earning history of a ticker
        "Get Ticker Info": Markup(f"<a href=\"/api/info/<name>\">/api/info/<name></a>"), #get the info of ticker
        "Get Update Script Master": Markup(f"<a href=\"/api/updateScriptMaster\">/api/updateScriptMaster</a>"), # it update the list of all the script in the market
        "Get Script Master": Markup(f"<a href=\"/api/instrumentList\">/api/instrumentList</a>"), #it return the all script in the market
        "Get Index List": Markup(f"<a href=\"/api/indexList\">/api/indexList</a>") #it return the list of all the index in the market
    
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
    elif period in ["3mo", "6mo", "1y","max","ytd"]:
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

@app.route("/api/instrumentList")
def Update_Script_Master():
    return instrumentList()

@app.route("/api/updateScriptMaster")
def Script_Master():
    response= updateMaster()
    if (response=='ok'):
      return ("success", 200)
    return ("error",400)

@app.route("/api/indexList")
def Index_List():
    res= indexList()
    if (res=='notok'):
      return ("error",400)
    return (res,200)

if __name__ == "__main__":
    app.run()
