
# %%
from NorenRestApiPy.NorenApi import  NorenApi
from flask import json
import pandas as pd
from dhanhq import dhanhq
import logging
import pyotp
from dotenv import load_dotenv
import os
from concurrent.futures import ThreadPoolExecutor, as_completed
import yfinance as yf
from constants import metaData

# Load environment variables from the .env file
load_dotenv()


import dotenv
def broker_holding():
#enable dbug to see request and responses
    # logging.basicConfig(level=logging.DEBUG)
    #generate the 2FA code using the secret key
    #you can use pyotp library to generate the 2FA code

    #credentials
    secret= os.getenv('SECRET_TOTP')
    totp = pyotp.TOTP(secret)
    user        = os.getenv('USER')
    u_pwd       = os.getenv('U_PWD')
    factor2     = totp.now() # => '492039'
    vc          = os.getenv('VC')
    app_key     = os.getenv('APP_KEY')
    imei        = os.getenv('IMET')
    access_token = os.getenv('DHAN_ACCESS_TOKEN')
    client_id=os.getenv('CLIENT_ID')
    #%%
    dhan = dhanhq(client_id=client_id,access_token=access_token)
    api = NorenApi( host='https://api.shoonya.com/NorenWClientTP/', websocket='wss://api.shoonya.com/NorenWSTP/') 

    totp.now() # => '492039'
    ret=api.login( userid=user,
        password=u_pwd,
        twoFA=factor2,
        vendor_code=vc,
        api_secret=app_key,
        imei=imei)


    # %%
    dhan_holdings = dhan.get_holdings()
    shoonya_holdings = api.get_holdings()

    holdingDfList=[]
    for holding in shoonya_holdings:
        data={
            "exchange":holding['exch_tsym'][0]['exch'],
            "tradingSymbol":holding['exch_tsym'][0]['tsym'].split("-")[0],
            "securityId":holding['exch_tsym'][0]['token'],
            "availableQty":holding['npoadqty'],
            "totalQty":holding['npoadqty'],
            "isin":holding['exch_tsym'][0]['isin'],
            "avgCostPrice":holding['upldprc'],
            "brokerName":"shoonya",
        }
        holdingDfList.append(data)

    # %%
    holdingDfList.extend(dhan_holdings['data'])
    df= pd.DataFrame(holdingDfList)
    dfcols=['exchange', 'tradingSymbol', 'securityId', 'availableQty', 'totalQty',
        'isin', 'avgCostPrice', 'brokerName']
    df=df.reindex(columns=dfcols)
    df['brokerName'] = df['brokerName'].fillna('dhan')
    df


    # %%
        
    BOList = ['INDIGRID']

    df['quote'] = df.apply(
        lambda row: f"{row['tradingSymbol']}.NS" 
        if row['exchange'] in ['NSE', 'ALL'] and row['tradingSymbol'] not in BOList 
        else f"{row['tradingSymbol']}.BO",
        axis=1
    )
    
    
    # Fetch function
    def fetch_live_data(row):
        quote = row['quote']
        try:
            ticker = yf.Ticker(quote)
            info = ticker.history_metadata
            result = {k: info.get(k, "") for k in metaData}
            sector = ticker.info.get('sector', "")
            return (quote, result, sector)
        except Exception as e:
            return (quote, {"error": str(e)}, "")

    # Use ThreadPoolExecutor
    live_data_map = {}
    sector_map = {}

    with ThreadPoolExecutor(max_workers=8) as executor:
        futures = {executor.submit(fetch_live_data, row): row['quote'] for _, row in df.iterrows()}
        for future in as_completed(futures):
            quote, data, sector = future.result()
            live_data_map[quote] = data
            sector_map[quote] = sector

    # Map both `liveData` and `sector` back to the DataFrame
    df['liveData'] = df['quote'].map(live_data_map)
    df['sector'] = df['quote'].map(sector_map)
    df['sector'] = df['sector'].replace('', pd.NA).fillna('unknown')

    res=json.loads(df.to_json(orient='records'))
    return res


# print(broker_holding())