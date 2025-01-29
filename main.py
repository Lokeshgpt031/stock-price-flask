import threading
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
import yfinance as yf
import json
from constants import *
from Stocklist import *
import uvicorn
from nse import NSE
from pathlib import Path
from datetime import datetime, timedelta
# Working directory


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", response_class=HTMLResponse)
def read_root():
    html_content = """
    <html>
        <head>
            <title>Stock API Endpoints</title>
            <style>
                table { width: 50%; border-collapse: collapse; margin: 20px 0; }
                th, td { border: 1px solid black; padding: 8px; text-align: left; }
                th { background-color: #f2f2f2; }
            </style>
        </head>
        <body>
            <h2>Stock API Endpoints</h2>
            <table>
                <tr><th>API Name</th><th>Endpoint</th></tr>
                <tr><td>Get Stock Price</td><td><a href="/api/stockprice/{name}">/api/stockprice/{name}</a></td></tr>
                <tr><td>Get Stock History</td><td><a href="/api/history/{name}/{period}">/api/history/{name}/{period}</a></td></tr>
                <tr><td>Get Earning History</td><td><a href="/api/earninghistory/{name}">/api/earninghistory/{name}</a></td></tr>
                <tr><td>Get Ticker Info</td><td><a href="/api/info/{name}">/api/info/{name}</a></td></tr>
                <tr><td>Get Update Script Master</td><td><a href="/api/updateScriptMaster">/api/updateScriptMaster</a></td></tr>
                <tr><td>Get Script Master</td><td><a href="/api/instrumentList">/api/instrumentList</a></td></tr>
                <tr><td>Get Index List</td><td><a href="/api/indexList">/api/indexList</a></td></tr>
            </table>
        </body>
    </html>
    """
    return HTMLResponse(content=html_content)


@app.get("/api/stockprice/{name}")
def get_stock_price(name: str):
    ticker = yf.Ticker(name).history_metadata
    datares = {i: ticker.get(i, "") for i in metaData}
    return datares

@app.get("/api/history/{name}/{period}")
def get_stock_history(name: str, period: str):
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

@app.get("/api/earninghistory/{name}")
def earning_history(name: str):
    ticker = yf.Ticker(name).earnings_history
    ticker.reset_index(inplace=True)
    ticker.rename(columns={"index": "Dates"}, inplace=True)
    return ticker.to_dict(orient='records')

@app.get("/api/info/{name}")
def get_ticker_info(name: str):
    return yf.Ticker(name).info

@app.get("/api/instrumentList")
def update_script_master():
    return instrumentList()

@app.get("/api/updateScriptMaster")
def script_master():
    response = updateMaster()
    return {"status": "success"} if response == "ok" else {"status": "error"}

@app.get("/api/indexList")
def index_list():
    res = indexList()
    return {"status": "success", "data": res} if res != "notok" else {"status": "error"}

@app.get("/crash")
def crash():
    return {"status": "error"}

@app.get("/api/announcement/{name}")
def get_announcement(name: str):
    try:
        DIR = Path(__file__).parent
        nse = NSE(download_folder=DIR)
        from_date = datetime.now() - timedelta(days=1)
        to_date = datetime.now()
        return JSONResponse(content=nse.announcements('equities', name, from_date=from_date, to_date=to_date))
    except Exception as e:
        return JSONResponse(content={"status": "error", "data": {"error": str(e)}})



if __name__ == "__main__":
    import uvicorn
    def run_server():
        uvicorn.run(app, host="localhost", port=8000)
    # run_server()
    server_thread = threading.Thread(target=run_server)
    server_thread.start()
    server_thread.join()
