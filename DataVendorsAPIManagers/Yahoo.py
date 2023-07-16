import os
import time
import progressbar
import numpy as np
import pandas as pd
import yfinance as yf
from commons import *
from base_classes import APIManager
from abc import ABC, abstractmethod
from typing import Union, Dict, List
from datetime import datetime, timedelta

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
    ) -> pd.DataFrame:
        assert len(tickers) > 0, 'tickers list is empty'
        assert end_datetime > start_datetime, f'start_datetime({start_datetime}) must be before end_datetime({end_datetime})'
        interval = DataYahoo.__get_valid_interval(interval)

        for i in range(len(tickers)):
            if tickers[i] in yfinance_benchmark_indices:
                tickers[i] = yfinance_benchmark_indices[tickers[i]]
            
        
        res_dict : Dict[str, str] = {}

        for ticker in tickers:
            res_dict[ticker] = yf.download()


    @staticmethod
    def get_data(
        index: str, 
        interval: int, 
        start_datetime: datetime, 
        end_datetime: datetime, 
        replace_close = False, 
        progress = False
    ) -> pd.DataFrame:
        '''Gets the tickers in the index, downloads the data, for each of them and processes those that are not empty before returning'''
        pass