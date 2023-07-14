import os
import time
import data_dicts
import progressbar
import numpy as np
import pandas as pd
import yfinance as yf
from io import StringIO
from requests import Session
from abc import ABC, abstractmethod
from typing import Union, Dict, List
from datetime import datetime, timedelta

class IndexLoader(ABC):
    __url_dict = {}

    @staticmethod
    @abstractmethod
    def get_url_dict():
        pass

    @staticmethod
    @abstractmethod
    def get_tickers(index : str) -> Dict[str, str]:
        pass

class APIManager(ABC):
    @staticmethod
    def __search(search_list : list, columns : pd.Index) -> Union[str, None]:
        for element in search_list:
            if element in columns:
                return element
        return None

    @staticmethod
    def process_OHLC_dataframe(
        dataframe : pd.DataFrame, 
        datetime_index = True,
        replace_close = False,
        capital_col_names = True,
    ) -> pd.DataFrame:
        df = dataframe.copy(deep = True)
        if datetime_index:
            if df.index.name in ['Date', 'date', 'Datetime', 'datetime']:
                if capital_col_names:
                    df.index.name = 'Datetime'
                else:
                    df.index.name = 'datetime'
            elif df.index.name == None:
                col_name = APIManager.__search(['Date', 'date', 'Datetime', 'datetime'], df.columns)
                df.set_index(col_name, inplace = True)
                df.index.name = 'datetime'

            if (type(df.index[0]) == str):
                df.index = pd.to_datetime(df.index)
        else:
            if df.index.name in ['Date', 'date', 'Datetime', 'datetime']:
                df = df.reset_index(drop = False)
        
        cap_names = True if 'High' in df.columns else False

        if cap_names and capital_col_names:
            if replace_close and 'Adj Close' in df.columns:
                df['Close'] = df['Adj Close'].values
        elif cap_names and not capital_col_names:
            if replace_close and 'Adj Close' in df.columns:
                df['Close'] = df['Adj Close'].values
                df.rename(columns = {
                        'Open':'open',
                        'High':'high',
                        'Low':'low',
                        'Close':'close',
                        'Adj Close':'adj close',
                        'Volume':'volume'
                    }, 
                    inplace=True
                )
        elif not cap_names and capital_col_names:
            if replace_close and 'adj close' in df.columns:
                df['close'] = df['adj close'].values
                df.rename(columns = {
                        'open':'Open',
                        'high':'High',
                        'low':'Low',
                        'close':'Close',
                        'adj close':'Adj Close',
                        'volume':'Volume'
                    }, 
                    inplace=True
                )
        else:
            if replace_close and 'adj Close' in df.columns:
                df['close'] = df['adj close'].values
        return df
    
    @abstractmethod
    def get_data():
        pass

class NSETickers(IndexLoader):
    __url_dict = {
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
    def get_url_dict():
        return NSETickers.__url_dict

    @staticmethod
    def get_tickers(index : str) -> Dict[str, str]:
        '''Downloads the index's current constituents from the NSE's website.'''
        assert index in NSETickers.__url_dict.keys(), f'\'{index}\' not in list of supported indexes. Use these \n {NSETickers.__url_dict.keys()}'

        try:
            session = Session()
            #Emulate browser
            session.headers.update({'user-agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.61 Safari/537.36"})
            # Get the cookies from the main page (will update automatically in headers)
            session.get('https://www.nseindia.com/')
            # Get the API data
            data = session.get(NSETickers.__url_dict[index]).text
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
