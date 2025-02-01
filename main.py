import threading
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from constants import *
from Stocklist import *
import uvicorn
from nse import NSE
from pathlib import Path
from datetime import datetime, timedelta
# Working directory
from FinanceClass import FinanceClass

finance=FinanceClass()

app = FastAPI( debug=True,
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
    return finance.get_stock_price(names=name.split(","))

@app.get("/api/info/{name}")
def get_ticker_info(name: str):
    return finance.get_ticker_info(names=name.split(","))

@app.get("/api/history/{name}/{period}")
def get_stock_history(name: str, period: str):
    return finance.get_stock_history(name=name,period=period)

@app.get("/api/annualEarning/{name}")
def earning_history(name: str):
    return finance.get_earning_report_annually()

@app.get("/api/quarterlyEarning/{name}")
def earning_history(name: str):
    return finance.get_earning_report_annually()

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
