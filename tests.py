import pandas as pd

from common.enums import NSE_URLS
from exchanges.nse import Nse


class TestNse:
    def test_get_tickers(self):
        nse = Nse()
        df = nse.get_tickers(index="NIFTY50")
        assert df.shape[0] == 50
