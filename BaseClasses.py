import numpy as np
import pandas as pd
from abc import ABC, abstractmethod
from typing import Union, Dict, List
from datetime import datetime, timedelta

class IndexLoader(ABC):
    @staticmethod
    @abstractmethod
    def get_url_dict() -> Dict[str, str]:
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
    
    @staticmethod
    @abstractmethod
    def __get_valid_interval():
        pass

    @staticmethod
    @abstractmethod
    def get_data(
        tickers : list, 
        interval : int, 
        exchange : str,
        start_datetime : datetime, 
        end_datetime : datetime, 
        replace_close = False, 
        progress = False
    ) -> Dict[str, pd.DataFrame]:
        pass

    @staticmethod
    @abstractmethod
    def get_data(
        index : str,
        interval : int,
        exchange : str,
        start_datetime : datetime,
        end_datetime : datetime,
        replace_close = False,
        progress = False,
    ) -> Dict[str, pd.DataFrame]:
        pass

