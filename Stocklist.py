
import requests
import pandas as pd
import json
import zipfile  # Corrected import statement
from io import BytesIO
import os

def download_and_process_symbols(url, filename):
    """Downloads, extracts, and saves symbol data to a CSV file."""
    response = requests.get(url, stream=True)
    zip_file = zipfile.ZipFile(BytesIO(response.content))
    with zip_file.open(filename) as txt_file:
        df = pd.read_csv(txt_file)
        # Save to CSV in the 'data' directory
        df.to_csv(os.path.join('./Source/', filename.replace(".txt",".csv")), index=False)



# from Source Folder. get csv files into pandas as merged

import glob

def combine_csv_files(directory):
    """Combines all CSV files in a directory into a single DataFrame."""
    all_files = glob.glob(os.path.join(directory, "*.csv"))
    if not all_files:
        return None
    li = []
    for filename in all_files:
        li.append(pd.read_csv(filename))
    frame = pd.concat(li, axis=0, ignore_index=True)
    return frame



def instrumentList():
    df = combine_csv_files("Source")
    df=df[df['Instrument'].isin(['INDEX', 'EQ'])]
    return df.to_json(orient='records')


def updateMaster():
    try:
        url_bse = 'https://api.shoonya.com/BSE_symbols.txt.zip'
        download_and_process_symbols(url_bse, 'BSE_symbols.txt')
        url_nse = 'https://api.shoonya.com/NSE_symbols.txt.zip'
        download_and_process_symbols(url_nse, 'NSE_symbols.txt')
        return "ok"
    except Exception as e:
        return "notok"

        
def indexList():
    try:
        df = combine_csv_files("Source")
        df=df[df['Instrument'].isin(['INDEX'])]
        return df.to_json(orient='records')
    except Exception as e:
        return "notok"