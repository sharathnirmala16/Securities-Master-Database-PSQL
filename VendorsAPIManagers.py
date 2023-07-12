import os
import time
import data_dicts
import progressbar
import numpy as np
import pandas as pd
import yfinance as yf
from io import StringIO
from requests import Session
from typing import Union, Dict, List
from datetime import datetime, timedelta

class NSETickers:
    url_dict = {
        'NIFTY50':'https://archives.nseindia.com/content/indices/ind_nifty50list.csv',
        'NIFTY100':'https://www.niftyindices.com/IndexConstituent/ind_nifty100list.csv',
        'NIFTY500':'https://archives.nseindia.com/content/indices/ind_nifty500list.csv',
        'NIFTYMIDCAP150':'https://www.niftyindices.com/IndexConstituent/ind_niftymidcap150list.csv',
        'NIFTYSMALLCAP250':'https://www.niftyindices.com/IndexConstituent/ind_niftysmallcap250list.csv',
        'NIFTYMICROCAP250':'https://www.niftyindices.com/IndexConstituent/ind_niftymicrocap250_list.csv',
        'NIFTYNEXT50':'https://archives.nseindia.com/content/indices/ind_niftynext50list.csv',
        'NIFTYBANK':'https://www.niftyindices.com/IndexConstituent/ind_niftybanklist.csv',
        'NIFTYIT':'https://www.niftyindices.com/IndexConstituent/ind_niftyitlist.csv',
        'NIFTYHEALTHCARE':'https://www.niftyindices.com/IndexConstituent/ind_niftyhealthcarelist.csv',
        'NIFTYFINSERVICE':'https://www.niftyindices.com/IndexConstituent/ind_niftyfinancelist.csv',
        'NIFTYAUTO':'https://www.niftyindices.com/IndexConstituent/ind_niftyautolist.csv',
        'NIFTYPHARMA':'https://www.niftyindices.com/IndexConstituent/ind_niftypharmalist.csv',
        'NIFTYFMCG':'https://www.niftyindices.com/IndexConstituent/ind_niftyfmcglist.csv',
        'NIFTYMEDIA':'https://www.niftyindices.com/IndexConstituent/ind_niftymedialist.csv',
        'NIFTYMETAL':'https://www.niftyindices.com/IndexConstituent/ind_niftymetallist.csv',
        'NIFTYREALTY':'https://www.niftyindices.com/IndexConstituent/ind_niftyrealtylist.csv'
    }

    @staticmethod
    def get_tickers(index : str) -> Dict[str, str]:
        '''Downloads the index's current constituents from the NSE's website.'''
        assert index in NSETickers.url_dict.keys(), f'\'{index}\' not in list of supported indexes. Use these \n {NSETickers.url_dict.keys()}'

        try:
            session = Session()
            #Emulate browser
            session.headers.update({'user-agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.61 Safari/537.36"})
            # Get the cookies from the main page (will update automatically in headers)
            session.get('https://www.nseindia.com/')
            # Get the API data
            data = session.get(NSETickers.url_dict[index]).text
            data = StringIO(data)
            df = pd.read_csv(data, sep = ',')
            n = df.shape[0]
            tickers_sector : Dict[str, str] = {}
            for i in range(n):
                tickers_sector[df['Symbol'][i]] = df['Industry'][i]
            return tickers_sector
        except Exception as e:
            print(e)

class DataYahoo:
    pass