import numpy as np
import pandas as pd
from commons import *
from io import StringIO
from requests import Session
from abc import ABC, abstractmethod
from base_classes import IndexLoader
from typing import Union, Dict, List
from datetime import datetime, timedelta

class NSETickers(IndexLoader):
    @staticmethod
    def get_url_dict() -> Dict[str, str]:
        return nse_url_dict

    @staticmethod
    def get_tickers(index : str) -> Dict[str, str]:
        '''Downloads the index's current constituents from the NSE's website.'''
        assert index in NSETickers.get_url_dict(), f'\'{index}\' not in list of supported indexes. Use these \n {NSETickers.get_url_dict().keys()}'

        try:
            session = Session()
            #Emulate browser
            session.headers.update({'user-agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.61 Safari/537.36"})
            # Get the cookies from the main page (will update automatically in headers)
            session.get('https://www.nseindia.com/')
            # Get the API data
            data = session.get(NSETickers.get_url_dict()[index]).text
            data = StringIO(data)
            df = pd.read_csv(data, sep = ',')
            n = df.shape[0]
            tickers_sector : Dict[str, str] = {}
            for i in range(n):
                tickers_sector[df['Symbol'][i]] = df['Industry'][i]
            return tickers_sector
        except Exception as e:
            print(e)