
# %%
from NorenRestApiPy.NorenApi import  NorenApi
from flask import json
import pandas as pd
from dhanhq import dhanhq
import logging
import pyotp
from dotenv import load_dotenv
import os

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
    dhan = dhanhq(client_id="TGLO12737J",access_token=access_token)
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
    df['quote'] = df.apply(lambda row: f"{row['tradingSymbol']}.NS" if row['exchange'] in ['NSE', 'ALL'] else f"{row['tradingSymbol']}.BO", axis=1)
    return json.loads(df.to_json(orient='records'))

    # %%
    # from FinanceClass import FinanceClass
    # finance = FinanceClass()
    # # df.quote.to_list()
    # output=finance.get_stock_price(df.quote.to_list())

    # res=pd.DataFrame(output)

    # # %%
    # cols=['symbol','regularMarketPrice', 'fiftyTwoWeekHigh', 'fiftyTwoWeekLow', 'previousClose',
    #     'regularMarketDayHigh', 'regularMarketDayLow', 'regularMarketVolume',
    #     'longName', 'shortName']


    # # %%
    # a = df.merge(res[cols], left_on='quote', right_on='symbol', how='inner')

    # return json.loads(a.to_json(orient='records'))


# print(broker_holding())