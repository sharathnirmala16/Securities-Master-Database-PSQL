import os
import time
import numpy as np
import pandas as pd
import yfinance as yf
import importlib
from commons import INTERVAL
from Exchanges.nse_tickers import NSETickers
from VendorsApiManagers.api_manager import APIManager
from typing import Union, Dict, List
from datetime import datetime, timedelta
from enum import Enum
from Exchanges.index_loader import IndexLoader
from commons import EXCHANGE, VENDOR, INTERVAL


class EXCHANGE_SUFFIX(Enum):
    NSE = "NS"
    BSE = "BO"


class YFINANCE_BENCHMARK_INDEX(Enum):
    NIFTY50 = "^NSEI"
    NIFTY100 = "^CNX100"
    NIFTY500 = "^CRSLDX"
    NIFTYMIDCAP150 = "NIFTYMIDCAP150.NS"
    NIFTYSMALLCAP250 = "NIFTYSMLCAP250.NS"
    NIFTYMICROCAP250 = "NIFTY_MICROCAP250.NS"
    NIFTYNEXT50 = "^NSMIDCP"
    NIFTYBANK = "^NSEBANK"
    NIFTYIT = "^CNXIT"
    NIFTYHEALTHCARE = "NIFTY_HEALTHCARE.NS"
    NIFTYFINSERVICE = "NIFTY_FIN_SERVICE.NS"
    NIFTYAUTO = "^CNXAUTO"
    NIFTYPHARMA = "^CNXPHARMA"
    NIFTYFMCG = "^CNXFMCG"
    NIFTYMEDIA = "^CNXMEDIA"
    NIFTYMETAL = "^CNXMETAL"
    NIFTYREALTY = "^CNXREALTY"


class YahooData(APIManager):
    def __init__(self, login_credentials: Dict[str, str]) -> None:
        super().__init__(login_credentials)

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
    def __download_data(
        tickers: list,
        exchange: str,
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

        start_date, end_date = start_datetime.strftime(
            "%Y-%m-%d"
        ), end_datetime.strftime("%Y-%m-%d")

        res_dict: Dict[str, str] = {}

        index_names = [index.name for index in YFINANCE_BENCHMARK_INDEX]
        formatted_tickers = list(
            map(
                lambda ticker: f"{ticker}.{getattr(EXCHANGE_SUFFIX, EXCHANGE(exchange).name).value}"
                if ticker not in index_names
                else getattr(YFINANCE_BENCHMARK_INDEX, ticker).value,
                tickers,
            )
        )

        if len(tickers) == 1:
            res_dict[tickers[0]] = yf.download(
                tickers=formatted_tickers,
                start=start_date,
                end=end_date,
                interval=interval,
                progress=progress,
            )
        else:
            for i, ticker in enumerate(tickers):
                try:
                    df = yf.download(
                        tickers=formatted_tickers[i],
                        start=start_date,
                        end=end_date,
                        interval=interval,
                        progress=False,
                    )
                    res_dict[ticker] = APIManager.process_OHLC_dataframe(
                        dataframe=df, replace_close=replace_close
                    )
                except Exception as e:
                    print(f"Error download data for {ticker}: {e}")

        return res_dict

    @staticmethod
    def get_data(
        interval: int,
        start_datetime: datetime,
        end_datetime: datetime,
        exchange: str,
        tickers: List[str] = None,
        index: str = None,
        replace_close=False,
        progress=False,
    ) -> Dict[str, pd.DataFrame]:
        """Gets the tickers in the index, downloads the data, for each of them and processes those that are not empty before returning"""
        if tickers is None and index is None:
            raise Exception("Either 'tickers' of 'index' must be given")
        if index is not None and tickers is None:
            exchange_obj: IndexLoader = getattr(
                importlib.import_module(
                    name=f"Exchanges.{EXCHANGE(exchange).name.lower()}_tickers"
                ),  # module name
                f"{EXCHANGE(exchange).name}Tickers",  # class name
            )
            tickers = list(
                map(
                    lambda ticker: f"{ticker}.{getattr(EXCHANGE_SUFFIX, EXCHANGE(exchange).name).value}",
                    exchange_obj.get_tickers(index=index).keys(),
                )
            )

        return YahooData.__download_data(
            tickers=tickers,
            exchange=exchange,
            interval=interval,
            start_datetime=start_datetime,
            end_datetime=end_datetime,
            replace_close=replace_close,
            progress=progress,
        )

    @staticmethod
    def get_vendor_ticker(ticker: str, exchange: str) -> str:
        return f"{ticker}.{getattr(EXCHANGE_SUFFIX, EXCHANGE(exchange).name).value}"

    @staticmethod
    def get_ticker_detail(ticker: str, exchange: str, detail: str) -> str:
        return yf.Ticker(YahooData.get_vendor_ticker(ticker, exchange)).info[detail]
