import threading
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
import yfinance as yf
import json
from constants import *
from Stocklist import *
import uvicorn
from nse import NSE
from pathlib import Path
from datetime import datetime, timedelta
# Working directory


app = FastAPI(
        title="My FastAPI App",
        description="This is a sample FastAPI application with Swagger documentation",
        version="1.0.0",
        contact={
            "name": "Stock Price Home",
            "email": "lokeshgptmbnr@outlook.com",
                                        },
                license_info={
                        "name": "MIT License",
                            }
             )


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", response_class=HTMLResponse)
def read_root():
    return RedirectResponse(url="/docs")
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

@app.get("/nseMarket")
def crash():
    from nse import NSE
    from pathlib import Path
    # Working directory
    DIR = Path(__file__).parent

    nse = NSE(download_folder=DIR)

    status = nse.status()

    nse.exit() # close requests session
    return status

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
