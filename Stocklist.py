
import os
import requests
import pandas as pd
import json
import zipfile  # Corrected import statement
from io import BytesIO
from vercel_blob import put
import vercel_blob
import dotenv

dotenv.load_dotenv()


def remove_Blobs():
    files=vercel_blob.list()
    files_list=files.get('blobs')
    print(files_list)
    for i in files_list:
        vercel_blob.delete(i['url'])
    return "Ok"

def download_and_process_symbols(url, filename):
    """Downloads, extracts, and saves symbol data to a CSV file."""
    response = requests.get(url, stream=True)
    zip_file = zipfile.ZipFile(BytesIO(response.content))
    with zip_file.open(filename) as txt_file:
        df = pd.read_csv(txt_file)
        csv_content = df.to_csv(index=False).encode()
        # Save the CSV to Vercel Blob
        file_path=filename.replace(".txt",".csv")
        put(path=file_path,data=csv_content,options= {
                "access": "public",
                "contentType": "text/csv",
                "fileName": file_path
                })

# url_nse = 'https://api.shoonya.com/NSE_symbols.txt.zip'

# download_and_process_symbols(url_nse, 'NSE_symbols.txt')



# from Source Folder. get csv files into pandas as merged

import glob

def combine_csv_files():
    try:
        """Combines all CSV files in a directory into a single DataFrame."""
        files=vercel_blob.list()
        files_list=files.get('blobs')
        # print(files)
        li = []
        for i in files_list:
            res=requests.get(vercel_blob.head(url=i['url']).get('downloadUrl'))
            # print(res.content)
            df = pd.read_csv(BytesIO(res.content))
            li.append(df)
        frame = pd.concat(li, axis=0, ignore_index=True)
        return frame
    except Exception as e:
        return "notok"


def instrumentList():
    df = combine_csv_files()
    df=df[df['Instrument'].isin(['INDEX', 'EQ'])]
    return df.to_json(orient='records')


def updateMaster():
    try:
        remove_Blobs()
        url_bse = 'https://api.shoonya.com/BSE_symbols.txt.zip'
        download_and_process_symbols(url_bse, 'BSE_symbols.txt')
        url_nse = 'https://api.shoonya.com/NSE_symbols.txt.zip'
        download_and_process_symbols(url_nse, 'NSE_symbols.txt')
        return "ok"
    except Exception as e:
        return "notok"
        
def indexList():
    try:
        df = combine_csv_files()
        df=df[df['Instrument'].isin(['INDEX'])]
        return df.to_json(orient='records')
    except Exception as e:
        return "notok"

