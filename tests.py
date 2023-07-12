import numpy as np
import pandas as pd
import secrets
import sqlalchemy
from sqlalchemy import sql
from datetime import datetime
from sql_commands import commands
from typing import Union, Dict, List
from credentials import psql_credentials
from SecuritiesMaster import *
from VendorsAPIManagers import *

#DataMaster instance
dm = DataMaster(psql_credentials['host'], psql_credentials['port'], psql_credentials['username'], psql_credentials['password'])

def update_table_test():
    print(dm.get_vendors_table())
    dm.update_vendor(old_name='Yahoo Finance', new_name='Yahoo Finance', website_url='https://finance.yahoo.com', support_email='@')    
    print(dm.get_vendors_table())
    dm.update_vendor(old_name='Yahoo Finance', new_name='Yahoo Finance', website_url='https://finance.yahoo.com', support_email='')
    print(dm.get_vendors_table())

def get_price_tables_tests():
    #Empty ticker test
    #print(dm.get_price_tables([], INTERVAL.m1, datetime.now(), datetime(2024,7,12,10,50,8)))

    #Invalid interval test
    #print(dm.get_price_tables([''], 5353, datetime.now(), datetime(2024,7,12,10,50,8)))

    #start_datetime > end_datetime()
    #print(dm.get_price_tables([''], INTERVAL.m1, datetime(2024,7,12,10,50,8), datetime.now()))
    
    #Vendor validity
    print(dm.get_price_tables([''], INTERVAL.m1, datetime.now(), datetime(2024,7,12,10,50,8), vendor='Any'))
    print(dm.get_price_tables([''], INTERVAL.m1, datetime.now(), datetime(2024,7,12,10,50,8), vendor='Yahoo Finance'))
    #print(dm.get_price_tables([''], INTERVAL.m1, datetime.now(), datetime(2024,7,12,10,50,8), vendor='yahoo finance'))

def test_get_tickers():
    print(NSETickers.get_tickers(index='NIFTY50'))
    print(NSETickers.get_tickers(index='NIFTYREALTY'))
    #print(NSETickers.get_tickers(index='NIFTYREALITY'))


#Main Code
test_get_tickers()