import threading
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.security import APIKeyHeader
from constants import *
from Stocklist import *
import uvicorn
from pathlib import Path
from datetime import datetime, timedelta
# Working directory
from FinanceClass import FinanceClass

from dotenv import load_dotenv
import os
load_dotenv()

ENV = os.getenv("ENV", "development")  # Default to 'development'
print(ENV)
finance=FinanceClass()

app = FastAPI(
    debug=True,
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





API_KEY = os.getenv("API_KEY", "development")  # Replace with your actual key
API_KEY_NAME = "x-api-key"

api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)



@app.middleware("http")
async def enforce_api_key(request: Request, call_next):
    allowed_paths = ["/docs", "/openapi.json", "/redoc"]
    if request.url.path in allowed_paths:
        return await call_next(request)
    
    api_key = request.headers.get(API_KEY_NAME)
    if api_key != API_KEY and ENV == 'production':
        return JSONResponse(status_code=403, content={"detail": "Invalid or missing API Key"})
    
    return await call_next(request)


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

@app.get("/api/stockPrice/{name}")
def get_stock_price(name: str):
    return finance.get_stock_price(symbols=name.split(","))

@app.get("/api/info/{name}")
def get_ticker_info(name: str):
    return finance.get_ticker_info(symbols=name.split(","))

@app.get("/api/history/{name}/{period}")
def get_stock_history(name: str, period: str):
    return finance.get_stock_history(symbol=name, period=period)

@app.get("/api/annualEarning/{name}")
def annual_earning_history(name: str):
    return finance.get_earning_report_annually(symbol=name)

@app.get("/api/quarterlyEarning/{name}")
def quarterly_earning_history(name: str):
    return finance.get_earning_report_quarterly(symbol=name)

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

from concurrent.futures import ThreadPoolExecutor

@app.get("/api/announcement/{name}")
def get_announcement(name: str, days: int = 1):
    try:
        from nse import NSE

        DIR = Path(__file__).parent
        nse = NSE(download_folder=DIR)
        from_date = datetime.now() - timedelta(days=days)
        to_date = datetime.now()
        names = [n.strip() for n in name.split(",") if n.strip()]

        def fetch_announcement(symbol):
            try:
                data = nse.announcements('equities', symbol, from_date=from_date, to_date=to_date)
                return {"symbol": symbol, "data": data,"TimeGenerated":datetime.strptime(data[0].get('sort_date'), "%Y-%m-%d %H:%M:%S").strftime("%Y-%m-%d %H:%M:%S")} if data!=[] else {"symbol": symbol, "data": data}
            except Exception as e:
                return {"symbol": symbol, "error": str(e),"TimeGenerated":datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

        with ThreadPoolExecutor() as executor:
            results = list(executor.map(fetch_announcement, names))

        nse.exit()
        return JSONResponse(content={
            "status": "success",
            "data": results,
            "TimeGenerated": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })
    except Exception as e:
        return JSONResponse(content={"status": "error", "data": {"error": str(e)}})


# @app.get("/api/holdings")
@app.get("/api/holdings", response_class=JSONResponse(content={"status": "success", "data": [], "TimeGenerated": datetime.now().strftime("%Y-%m-%d %H:%M:%S")}))
def get_holdings():
    import brokers
    try:
        holdings = brokers.broker_holding()
        return JSONResponse(content={"status": "success", "data": holdings, "TimeGenerated": datetime.now().strftime("%Y-%m-%d %H:%M:%S")})
    except Exception as e:
        return JSONResponse(content={"status": "error", "data": {"error": str(e)}})

@app.get("/api/ai/SummarizeDocument")
def SummarizeDocument(url:str):
    from AI.pdfToText import fullflow
    return fullflow(url=url)







if __name__ == "__main__":
    import uvicorn
    def run_server():
        uvicorn.run(app, host="localhost", port=8000)
    # run_server()
    server_thread = threading.Thread(target=run_server)
    server_thread.start()
    server_thread.join()
