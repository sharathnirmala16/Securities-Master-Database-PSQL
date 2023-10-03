import pytz
import secrets
import sqlalchemy
import numpy as np
import pandas as pd
from sqlalchemy import sql
from datetime import datetime
from sql_commands import commands
from typing import Union, Dict, List
from credentials import psql_credentials
from securities_master import *
from base_classes import *
from exchanges import *

# DataMaster instance
dm = SecuritiesMaster(
    psql_credentials["host"],
    psql_credentials["port"],
    psql_credentials["username"],
    psql_credentials["password"],
)


def update_table_test():
    print(dm.get_vendors_table())
    dm.update_vendor(
        old_name="Yahoo Finance",
        new_name="Yahoo Finance",
        website_url="https://finance.yahoo.com",
        support_email="@",
    )
    print(dm.get_vendors_table())
    dm.update_vendor(
        old_name="Yahoo Finance",
        new_name="Yahoo Finance",
        website_url="https://finance.yahoo.com",
        support_email="",
    )
    print(dm.get_vendors_table())


def get_price_tables_tests():
    # Empty ticker test
    # print(dm.get_price_tables([], INTERVAL.m1, datetime.now(), datetime(2024,7,12,10,50,8)))

    # Invalid interval test
    # print(dm.get_price_tables([''], 5353, datetime.now(), datetime(2024,7,12,10,50,8)))

    # start_datetime > end_datetime()
    # print(dm.get_price_tables([''], INTERVAL.m1, datetime(2024,7,12,10,50,8), datetime.now()))

    # Vendor validity
    print(
        dm.get_price_tables(
            [""],
            INTERVAL.m1,
            datetime.now(),
            datetime(2024, 7, 12, 10, 50, 8),
            vendor="Any",
        )
    )
    print(
        dm.get_price_tables(
            [""],
            INTERVAL.m1,
            datetime.now(),
            datetime(2024, 7, 12, 10, 50, 8),
            vendor="Yahoo Finance",
        )
    )
    # print(dm.get_price_tables([''], INTERVAL.m1, datetime.now(), datetime(2024,7,12,10,50,8), vendor='yahoo finance'))


def test_get_tickers():
    print(NSETickers.get_url_dict())
    print(NSETickers.get_tickers(index="NIFTY50"))
    print(NSETickers.get_tickers(index="NIFTYREALTY"))
    # print(NSETickers.get_tickers(index='NIFTYREALITY'))


from DVApiManagers.yahoo import YahooData

print(
    YahooData.get_data(
        index="NIFTY50",
        interval=INTERVAL.m5.value,
        start_datetime=datetime(2023, 9, 3),
        end_datetime=datetime(2023, 10, 3),
        progress=True,
    )
)
