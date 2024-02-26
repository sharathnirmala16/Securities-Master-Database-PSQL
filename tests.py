import pytest
import numpy as np
import pandas as pd
import yfinance as yf

from common.enums import *
from common.exceptions import *
from datetime import datetime
from exchanges.nse import Nse
from vendors.vendor import Vendor
from vendors.yahoo import Yahoo


class TestNse:
    def setup_method(self):
        self.nse = Nse()

    def test_get_symbols(self):
        tickers = self.nse.get_symbols(index="NIFTY50")
        assert len(tickers) == 50 and isinstance(tickers, dict)

        with pytest.raises(ValueError):
            df = self.nse.get_symbols(index="EXCEPTION")

    def test_get_symbols_detailed(self):
        data = self.nse.get_symbols_detailed(index="NIFTY50")
        assert data.shape[0] == 50

        with pytest.raises(ValueError):
            df = self.nse.get_symbols_detailed(index="EXCEPTION")


class TestYahoo:
    def setup_method(self):
        self.nse = Nse()
        self.yahoo = Yahoo({})

    @pytest.mark.download_required
    def test_get_adjusted_values(self):
        df_original = yf.download(
            ["RELIANCE.NS"], interval="1d", period="10y", progress=False
        )
        df_adjusted = self.yahoo.get_adjusted_values(df_original)
        original_networth = df_original["Close"] * df_original["Volume"]
        adjusted_networth = df_adjusted["Close"] * df_adjusted["Volume"]

        assert (
            original_networth.iloc[0] == adjusted_networth.iloc[0]
            and original_networth.iloc[-1] == adjusted_networth.iloc[-1]
        )

    @pytest.mark.download_required
    def test_get_data_index_only(self):
        df_orig: pd.DataFrame = yf.download(
            tickers=["^NSEI"],
            start="2024-01-01",
            end="2024-02-01",
            interval="1d",
            progress=False,
        )
        df_my_lib = self.yahoo.get_data(
            interval=INTERVAL.d1,
            exchange=self.nse,
            start_datetime=datetime(2024, 1, 1),
            end_datetime=datetime(2024, 2, 1),
            symbols=["NIFTY50"],
        )

        assert df_orig.equals(df_my_lib["NIFTY50"])

    @pytest.mark.download_required
    def test_get_data_index_constitutents(self):
        data = self.yahoo.get_data(
            interval=INTERVAL.d1,
            exchange=self.nse,
            start_datetime=datetime(2024, 1, 1),
            end_datetime=datetime(2024, 2, 1),
            index="NIFTY50",
        )

        assert len(data) == 50 and data[list(data.keys())[0]].shape[0] > 5

    @pytest.mark.download_required
    def test_get_data_mixed_symbols(self):
        symbols = ["TATAMOTORS", "NIFTY50"]
        data = self.yahoo.get_data(
            interval=INTERVAL.d1,
            exchange=self.nse,
            start_datetime=datetime(2024, 1, 1),
            end_datetime=datetime(2024, 2, 1),
            symbols=symbols,
        )

        assert (
            len(data) == 2
            and list(data.keys()) == symbols
            and data[list(data.keys())[0]].shape[0] > 5
            and data[list(data.keys())[1]].shape[0] > 5
        )

    @pytest.mark.download_required
    def test_get_data_adj_prices_single(self):
        symbols = ["TATAMOTORS"]
        data_adj = self.yahoo.get_data(
            interval=INTERVAL.d1,
            exchange=self.nse,
            start_datetime=datetime(2014, 1, 1),
            end_datetime=datetime(2024, 1, 1),
            symbols=symbols,
            adjusted_prices=True,
        )
        data_orig = self.yahoo.get_data(
            interval=INTERVAL.d1,
            exchange=self.nse,
            start_datetime=datetime(2014, 1, 1),
            end_datetime=datetime(2024, 1, 1),
            symbols=symbols,
            adjusted_prices=False,
        )

        assert (
            data_orig["TATAMOTORS"].shape[1] > data_adj["TATAMOTORS"].shape[1]
            and data_orig["TATAMOTORS"]["Close"].iloc[0]
            != data_adj["TATAMOTORS"]["Close"].iloc[0]
        )

    @pytest.mark.download_required
    def test_get_data_adj_prices_multi(self):
        symbols = ["TATAMOTORS", "RELIANCE"]
        data_adj = self.yahoo.get_data(
            interval=INTERVAL.d1,
            exchange=self.nse,
            start_datetime=datetime(2014, 1, 1),
            end_datetime=datetime(2024, 1, 1),
            symbols=symbols,
            adjusted_prices=True,
        )
        data_orig = self.yahoo.get_data(
            interval=INTERVAL.d1,
            exchange=self.nse,
            start_datetime=datetime(2014, 1, 1),
            end_datetime=datetime(2024, 1, 1),
            symbols=symbols,
            adjusted_prices=False,
        )

        assert (
            data_orig["TATAMOTORS"].shape[1] > data_adj["TATAMOTORS"].shape[1]
            and data_orig["TATAMOTORS"]["Close"].iloc[0]
            != data_adj["TATAMOTORS"]["Close"].iloc[0]
        ) and (
            data_orig["RELIANCE"].shape[1] > data_adj["RELIANCE"].shape[1]
            and data_orig["RELIANCE"]["Close"].iloc[0]
            != data_adj["RELIANCE"]["Close"].iloc[0]
        )

    @pytest.mark.download_required
    def test_get_data_adj_prices_drop_single(self):
        symbols = ["TATAMOTORS"]
        data_adj = self.yahoo.get_data(
            interval=INTERVAL.d1,
            exchange=self.nse,
            start_datetime=datetime(2014, 1, 1),
            end_datetime=datetime(2024, 2, 1),
            symbols=symbols,
            adjusted_prices=True,
        )

        assert "Adj Close" not in data_adj["TATAMOTORS"].columns

    @pytest.mark.download_required
    def test_get_data_adj_prices_drop_multi(self):
        symbols = ["TATAMOTORS", "RELIANCE"]
        data_adj = self.yahoo.get_data(
            interval=INTERVAL.d1,
            exchange=self.nse,
            start_datetime=datetime(2024, 1, 1),
            end_datetime=datetime(2024, 2, 1),
            symbols=symbols,
            adjusted_prices=True,
        )

        assert (
            "Adj Close" not in data_adj["TATAMOTORS"].columns
            and "Adj Close" not in data_adj["RELIANCE"]
        )

    def test_get_data_errors(self):
        symbols = ["TCS"]
        with pytest.raises(AttributeError):
            self.yahoo.get_data(
                interval=INTERVAL.y1,
                exchange=self.nse,
                start_datetime=datetime(2024, 1, 1),
                end_datetime=datetime(2024, 2, 1),
                adjusted_prices=True,
            )
        with pytest.raises(ValueError):
            self.yahoo.get_data(
                interval=INTERVAL.y1,
                exchange=self.nse,
                start_datetime=datetime(2024, 1, 1),
                end_datetime=datetime(2024, 2, 1),
                symbols=[],
                adjusted_prices=True,
            )
        with pytest.raises(ValueError):
            self.yahoo.get_data(
                interval=INTERVAL.y1,
                exchange=self.nse,
                symbols=["TCS"],
                start_datetime=datetime(2024, 1, 2),
                end_datetime=datetime(2024, 1, 1),
            )
        with pytest.raises(ValueError):
            self.yahoo.get_data(
                interval=INTERVAL.y1,
                exchange=self.nse,
                start_datetime=datetime(2024, 1, 1),
                end_datetime=datetime(2024, 2, 1),
                symbols=symbols,
                adjusted_prices=True,
            )

    def test_get_vendor_ticker(self):
        assert self.yahoo.get_vendor_ticker("TCS", self.nse) == "TCS.NS"

    def test_get_symbol_details(self):
        assert len(self.yahoo.get_symbol_details("TCS", self.nse)) > 0
