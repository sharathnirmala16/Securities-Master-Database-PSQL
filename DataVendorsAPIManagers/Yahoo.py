import os
import time
import progressbar
import numpy as np
import pandas as pd
import yfinance as yf
from commons import *
from Exchanges import *
from BaseClasses import APIManager
from abc import ABC, abstractmethod
from typing import Union, Dict, List
from SecuritiesMaster import DataMaster
from datetime import datetime, timedelta
from credentials import psql_credentials

class DataYahoo(APIManager):
    @staticmethod
    def __get_valid_interval(interval : int) -> str:
        intervals = { v:m for v, m in vars(INTERVAL).items() if not (v.startswith('_')  or callable(m)) }
        valid_intervals = {
            intervals['m1'] : '1m',
            intervals['m5'] : '5m',
            intervals['m15'] : '15m',
            intervals['m30'] : '30m',
            intervals['h1'] : '1h',
            intervals['d1'] : '1d',
            intervals['w1'] : '1wk',
            intervals['mo1'] : '1mo',
            intervals['y1'] : 'y1',
        }
        assert interval in valid_intervals.keys(), f'{int} interval not supported'
        return valid_intervals[interval]

    @staticmethod
    def __download_data(
        tickers : list,
        interval : int,
        start_datetime : datetime,
        end_datetime : datetime,
        replace_close = False,
        progress = False
    ) -> Dict[str, pd.DataFrame]:
        assert len(tickers) > 0, 'tickers list is empty'
        assert end_datetime > start_datetime, f'start_datetime({start_datetime}) must be before end_datetime({end_datetime})'
        interval = DataYahoo.__get_valid_interval(interval)

        for i in range(len(tickers)):
            if tickers[i] in yfinance_benchmark_indices:
                tickers[i] = yfinance_benchmark_indices[tickers[i]]
            
        start_date , end_date : str = start_datetime.strftime('%Y-%m-%d'), end_datetime.strftime('%Y-%m-%d')

        res_dict : Dict[str, str] = {}

        if len(tickers) == 1:
            res_dict[tickers[0]] = yf.download(
                tickers=tickers, 
                start=start_date, 
                end=end_date, 
                interval=interval,
                progress=progress
            )
        else:
            #progress bar code
            progress_bar_widget = [
                ' [', progressbar.Timer(format= 'elapsed time: %(elapsed)s'), '] ', 
                progressbar.Bar('*'),
                ' (', progressbar.ETA(), ') ', 
                progressbar.Percentage()
            ]
            bar = progressbar.ProgressBar(max_value = len(tickers), widgets = progress_bar_widget).start()
            step_count = 0
            for ticker in tickers:
                try:
                    df = yf.download(
                        tickers=ticker, 
                        start=start_date, 
                        end=end_date, 
                        interval=interval,
                        progress=False
                    )
                    res_dict[ticker] = APIManager.process_OHLC_dataframe(dataframe = df, replace_close = replace_close)
                except Exception as e:
                    print(e)
                if progress:
                    step_count += 1
                    bar.update(step_count)
        
        return res_dict

    @staticmethod
    def get_data(
        tickers : list, 
        interval: int, 
        start_datetime: datetime, 
        end_datetime: datetime, 
        replace_close = False, 
        progress = False
    ) -> Dict[str, pd.DataFrame]:
        '''Gets the tickers in the index, downloads the data, for each of them and processes those that are not empty before returning'''
        return DataYahoo.__download_data(
            tickers, 
            interval, 
            start_datetime, 
            end_datetime, 
            replace_close, 
            progress
        )

    @staticmethod
    def get_data(
        index: str, 
        interval: int, 
        start_datetime: datetime, 
        end_datetime: datetime, 
        replace_close = False, 
        progress = False
    ) -> Dict[str, pd.DataFrame]:
        '''Gets the tickers in the index, downloads the data, for each of them and processes those that are not empty before returning'''
        tickers = NSETickers.get_tickers(index=index)
        return DataYahoo.__download_data(
            tickers, 
            interval, 
            start_datetime, 
            end_datetime, 
            replace_close, 
            progress
        )