import pytz
import numpy as np
import pandas as pd
from datetime import datetime
from SecuritiesMaster import DataMaster
from credentials import psql_credentials

dm = DataMaster(psql_credentials['host'], psql_credentials['port'], psql_credentials['username'], psql_credentials['password'])

def add_yahoo_vendor():
    dm.add_vendor(name='Yahoo Finance', website_url='https://finance.yahoo.com', support_email='')

def add_bse_exchange():
    dm.add_exchange(
        abbreviation='BSE',
        name = 'Bombay Stock Exchange',
        website_url = 'https://www.bseindia.com',
        city = 'Mumbai',
        country = 'India',
        currency = 'INR', 
        time_zone_offset = datetime.now(pytz.timezone('Asia/Kolkata')).utcoffset()
    )

def add_nse_exchange():
    dm.add_exchange(
        abbreviation = 'NSE',
        name = 'National Stock Exchange',
        website_url = 'https://www.nseindia.com',
        city = 'New Delhi',
        country = 'India',
        currency = 'INR',
        time_zone_offset = datetime.now(pytz.timezone('Asia/Kolkata')).utcoffset()
    )

def add_nse_indices():
    url_dict = {
        'NIFTY50':'https://archives.nseindia.com/content/indices/ind_nifty50list.csv',
        'NIFTY100':'https://www.niftyindices.com/IndexConstituent/ind_nifty100list.csv',
        'NIFTY500':'https://archives.nseindia.com/content/indices/ind_nifty500list.csv',
        'NIFTYMIDCAP150':'https://www.niftyindices.com/IndexConstituent/ind_niftymidcap150list.csv',
        'NIFTYSMALLCAP250':'https://www.niftyindices.com/IndexConstituent/ind_niftysmallcap250list.csv',
        'NIFTYMICROCAP250':'https://www.niftyindices.com/IndexConstituent/ind_niftymicrocap250_list.csv',
        'NIFTYNEXT50':'https://archives.nseindia.com/content/indices/ind_niftynext50list.csv',
        'NIFTYBANK':'https://www.niftyindices.com/IndexConstituent/ind_niftybanklist.csv',
        'NIFTYIT':'https://www.niftyindices.com/IndexConstituent/ind_niftyitlist.csv',
        'NIFTYHEALTHCARE':'https://www.niftyindices.com/IndexConstituent/ind_niftyhealthcarelist.csv',
        'NIFTYFINSERVICE':'https://www.niftyindices.com/IndexConstituent/ind_niftyfinancelist.csv',
        'NIFTYAUTO':'https://www.niftyindices.com/IndexConstituent/ind_niftyautolist.csv',
        'NIFTYPHARMA':'https://www.niftyindices.com/IndexConstituent/ind_niftypharmalist.csv',
        'NIFTYFMCG':'https://www.niftyindices.com/IndexConstituent/ind_niftyfmcglist.csv',
        'NIFTYMEDIA':'https://www.niftyindices.com/IndexConstituent/ind_niftymedialist.csv',
        'NIFTYMETAL':'https://www.niftyindices.com/IndexConstituent/ind_niftymetallist.csv',
        'NIFTYREALTY':'https://www.niftyindices.com/IndexConstituent/ind_niftyrealtylist.csv'
    }

    for key in url_dict.keys():
        name = key.replace('NIFTY', '').lower()
        sector = key.replace('NIFTY', '').lower()
        if any(chr.isdigit() for chr in name):
            name += 'top stocks'
            sector = 'all'

        dm.add_symbol(
            exchange = 'National Stock Exchange',
            ticker = key,
            instrument = 'Index',
            name = name,
            sector = sector,
            currency = 'INR'
        )

def temp_script():
    dm.temp()

add_nse_indices()