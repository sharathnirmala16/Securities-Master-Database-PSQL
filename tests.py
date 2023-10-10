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
from Exchanges.index_loader import *
from Exchanges.nse_tickers import *

# DataMaster instance
dm = SecuritiesMaster(
    psql_credentials["host"],
    psql_credentials["port"],
    psql_credentials["username"],
    psql_credentials["password"],
)


# def update_table_test():
#     print(dm.get_vendors_table())
#     dm.update_vendor(
#         old_name="Yahoo Finance",
#         new_name="Yahoo Finance",
#         website_url="https://finance.yahoo.com",
#         support_email="@",
#     )
#     print(dm.get_vendors_table())
#     dm.update_vendor(
#         old_name="Yahoo Finance",
#         new_name="Yahoo Finance",
#         website_url="https://finance.yahoo.com",
#         support_email="",
#     )
#     print(dm.get_vendors_table())


# def get_price_tables_tests():
#     # Empty ticker test
#     # print(dm.get_price_tables([], INTERVAL.m1, datetime.now(), datetime(2024,7,12,10,50,8)))

#     # Invalid interval test
#     # print(dm.get_price_tables([''], 5353, datetime.now(), datetime(2024,7,12,10,50,8)))

#     # start_datetime > end_datetime()
#     # print(dm.get_price_tables([''], INTERVAL.m1, datetime(2024,7,12,10,50,8), datetime.now()))

#     # Vendor validity
#     print(
#         dm.get_price_tables(
#             [""],
#             INTERVAL.m1,
#             datetime.now(),
#             datetime(2024, 7, 12, 10, 50, 8),
#             vendor="Any",
#         )
#     )
#     print(
#         dm.get_price_tables(
#             [""],
#             INTERVAL.m1,
#             datetime.now(),
#             datetime(2024, 7, 12, 10, 50, 8),
#             vendor="Yahoo Finance",
#         )
#     )
#     # print(dm.get_price_tables([''], INTERVAL.m1, datetime.now(), datetime(2024,7,12,10,50,8), vendor='yahoo finance'))


# def test_get_tickers():
#     print(NSETickers.get_url_dict())
#     print(NSETickers.get_tickers(index="NIFTY50"))
#     print(NSETickers.get_tickers(index="NIFTYREALTY"))
#     # print(NSETickers.get_tickers(index='NIFTYREALITY'))


# from VendorsApiManagers.api_manager import APIManager
# from commons import VENDOR
# import importlib

# vendor = VENDOR.YAHOO.value
# class_obj: APIManager = getattr(
#     importlib.import_module(name=f"VendorsApiManagers.{VENDOR(vendor).name.lower()}"),
#     f"{VENDOR(vendor).name[0:1] + VENDOR(vendor).name[1:].lower()}Tickers",
# )

# df = class_obj.get_data(
#     tickers=["TCS.NS"],
#     interval=INTERVAL.d1.value,
#     exchange=EXCHANGE.NSE.value,
#     start_datetime=datetime(2018, 1, 1),
#     end_datetime=datetime(2019, 1, 1),
# )
# print(df)


# class Base(ABC):
#     _string: str

#     def __init__(self, string) -> None:
#         self._string = string

#     @abstractmethod
#     def print_string(self) -> None:
#         pass


# class Child(Base):
#     def __init__(self, string) -> None:
#         super().__init__(string)

#     def print_string(self) -> None:
#         print(self._string)


# c = Child("Hello")
# c.print_string()

import time

t1 = time.time()
data = dm.get_prices(
    interval=INTERVAL.d1.value,
    start_datetime=datetime(2018, 1, 1),
    end_datetime=datetime(2023, 1, 1),
    vendor=VENDOR.YAHOO.value,
    exchange=EXCHANGE.NSE.value,
    instrument=INSTRUMENT.STOCK.value,
    index="NIFTY50",
    cache_data=True,
)
t2 = time.time()

print(data)
print(f"Execution Time: {t2 - t1}s")
