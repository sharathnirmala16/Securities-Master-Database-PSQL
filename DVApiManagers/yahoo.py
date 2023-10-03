import os
import time
import progressbar
import numpy as np
import pandas as pd
import yfinance as yf
from commons import INTERVAL, YFINANCE_BENCHMARK_INDEX
from exchanges import NSETickers, BSETickers
from base_classes import APIManager
from abc import ABC, abstractmethod
from typing import Union, Dict, List
from securities_master import SecuritiesMaster
from datetime import datetime, timedelta
from credentials import psql_credentials


class YahooData(APIManager):
    @staticmethod
    def __get_valid_interval(interval: int) -> str:
        intervals = {interval.name: interval.value for interval in INTERVAL}
        valid_intervals = {
            intervals["m1"]: "1m",
            intervals["m5"]: "5m",
            intervals["m15"]: "15m",
            intervals["m30"]: "30m",
            intervals["h1"]: "1h",
            intervals["d1"]: "1d",
            intervals["w1"]: "1wk",
            intervals["mo1"]: "1mo",
            intervals["y1"]: "y1",
        }

        if interval not in valid_intervals:
            raise Exception(f"{int} interval not supported")
        return valid_intervals[interval]

    @staticmethod
    def __get_yf_indices() -> Dict[str, str]:
        return {index.name: index.value for index in YFINANCE_BENCHMARK_INDEX}

    @staticmethod
    def __download_data(
        tickers: list,
        interval: int,
        start_datetime: datetime,
        end_datetime: datetime,
        replace_close=False,
        progress=False,
    ) -> Dict[str, pd.DataFrame]:
        if len(tickers) < 0:
            raise Exception("tickers list is empty")
        if end_datetime < start_datetime:
            raise Exception(
                f"start_datetime({start_datetime}) must be before end_datetime({end_datetime})"
            )
        interval = YahooData.__get_valid_interval(interval)

        indices = YahooData.__get_yf_indices()
        for i in range(len(tickers)):
            if tickers[i] in indices.keys():
                tickers[i] = indices[tickers[i]]

        start_date, end_date = start_datetime.strftime(
            "%Y-%m-%d"
        ), end_datetime.strftime("%Y-%m-%d")

        res_dict: Dict[str, str] = {}

        if len(tickers) == 1:
            res_dict[tickers[0]] = yf.download(
                tickers=tickers,
                start=start_date,
                end=end_date,
                interval=interval,
                progress=progress,
            )
        else:
            # progress bar code
            progress_bar_widget = [
                " [",
                progressbar.Timer(format="elapsed time: %(elapsed)s"),
                "] ",
                progressbar.Bar("*"),
                " (",
                progressbar.ETA(),
                ") ",
                progressbar.Percentage(),
            ]
            bar = progressbar.ProgressBar(
                max_value=len(tickers), widgets=progress_bar_widget
            ).start()
            step_count = 0
            for ticker in tickers:
                try:
                    df = yf.download(
                        tickers=ticker,
                        start=start_date,
                        end=end_date,
                        interval=interval,
                        progress=False,
                    )
                    res_dict[ticker] = APIManager.process_OHLC_dataframe(
                        dataframe=df, replace_close=replace_close
                    )
                except Exception as e:
                    print(e)
                if progress:
                    step_count += 1
                    bar.update(step_count)

        return res_dict

    @staticmethod
    def __yf_format_tickers(tickers: List[str], exchange: str) -> List[str]:
        suffix = ""
        if exchange == "NSE":
            suffix = "NS"

        return [f"{ticker}.{suffix}" for ticker in tickers]

    @staticmethod
    def get_data(
        interval: int,
        start_datetime: datetime,
        end_datetime: datetime,
        tickers: List[str] = None,
        index: str = None,
        exchange: str = "NSE",
        replace_close=False,
        progress=False,
    ) -> Dict[str, pd.DataFrame]:
        """Gets the tickers in the index, downloads the data, for each of them and processes those that are not empty before returning"""
        if tickers is None and index is None:
            raise Exception("Either 'tickers' of 'index' must be given")
        if index is not None and tickers is None:
            tickers = YahooData.__yf_format_tickers(
                list(NSETickers.get_tickers(index=index).keys()), exchange=exchange
            )
        return YahooData.__download_data(
            tickers, interval, start_datetime, end_datetime, replace_close, progress
        )
