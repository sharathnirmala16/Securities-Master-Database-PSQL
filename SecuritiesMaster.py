import numpy as np
import pandas as pd
import secrets
import sqlalchemy
from sqlalchemy import sql
from datetime import datetime
from sql_commands import commands
from typing import Union, Dict, List
from credentials import psql_credentials

class INTERVAL:
    ms1 = 1
    ms5 = 5
    ms10 = 10
    ms100 = 100
    ms500 = 500
    s1 = 1000
    s5 = 5000
    s15 = 15000
    s30 = 30000
    m1 = 60000
    m5 = 300000
    m15 = 900000
    m30 = 1800000
    h1 = 3600000
    h4 = 14400000
    d1 = 86400000
    w1 = 604800000
    mo1 = 2592000000
    y1 = 31104000000

class DataMaster:
    '''
    User can create an instance of this class to obtain data
    '''
    def __init__(self, host : str, port : int, username : str, password : str, progress = False) -> None:
        '''
        Creates the necessary database connection objects.
        '''
        try:
            self.__url = f'postgresql+psycopg2://{username}:{password}@{host}:{port}/securities_master'
            self.__engine = sqlalchemy.create_engine(self.__url, isolation_level='AUTOCOMMIT')
            self.__create_base_tables()
        
            #Converts the INTERVAL class into a dictionary for reference inside the DataMaster class.
            self.__intervals = { v:m for v, m in vars(INTERVAL).items() if not (v.startswith('_')  or callable(m)) }
        except Exception as e:
            print(e)

    def __create_base_tables(self) -> None:
        '''
        Specifically for creating the base tables that are 
        necessary for basic operations.
        '''
        try:
            for command in commands.values():
                with self.__engine.connect() as conn:
                    conn.execute(sql.text(command))
        except Exception as e:
            print(e)

    def __verify_vendor(self, vendor : str) -> bool:
        vendors_list = self.get_vendors_table()['name']
        if vendor in vendors_list.values or vendor == 'Any':
            return True
        return False

    def __search_valid_vendor(
        self, 
        ticker : str, 
        interval : int, 
        start_datetime : datetime,
        end_datetime : datetime
    ) -> str:
        '''
        If \'Any\' is chosen for vendor, tries to find the vendor 
        with the data for given input.
        '''
        pass

    def __get_ticker_data(
        self,
        ticker : str,
        interval : int,
        start_datetime : datetime,
        end_datetime : datetime,
        vendor : str,
        progress : bool,
        download_missing : bool
    ) -> Union[pd.DataFrame, None]:
        pass

    def get_exchange_table(self) -> pd.DataFrame:
        try:
            return pd.read_sql_query(sql = 'SELECT * FROM Exchange;', con = self.__engine)
        except Exception as e:
            print(e)

    def get_vendors_table(self) -> pd.DataFrame:
        try:
            return pd.read_sql_query(sql = 'SELECT * FROM DataVendor;', con = self.__engine)
        except Exception as e:
            print(e)
    
    def get_symbol_table(self) -> pd.DataFrame:
        try:
            return pd.read_sql_query(sql = 'SELECT * FROM Symbol;', con = self.__engine)
        except Exception as e:
            print(e)
    
    def add_vendor(self, name : str, website_url : str, support_email : str) -> None:
        try:
            with self.__engine.connect() as conn:
                conn.execute(sql.text(
                    f'''
                    INSERT INTO DataVendor 
                    (name, website_url, support_email, created_datetime, last_updated_datetime) 
                    VALUES
                    ('{name}', '{website_url}', '{support_email}', '{datetime.now()}', '{datetime.now()}');
                    '''
                ))
        except Exception as e:
            print(e)

    def update_vendor(self, old_name : str, new_name : str, website_url : str, support_email : str) -> None:
        try:
            with self.__engine.connect() as conn:
                conn.execute(sql.text(
                    f'''
                    UPDATE DataVendor 
                    SET 
                    name = '{new_name}', 
                    website_url = '{website_url}', 
                    support_email = '{support_email}',
                    last_updated_datetime = '{datetime.now()}'
                    WHERE name = '{old_name}';
                    '''
                ))
        except Exception as e:
            print(e)

    def get_price_tables(
        self,
        tickers : List[str],
        interval : int,
        start_datetime : datetime,
        end_datetime : datetime,
        vendor = 'Any',
        progress = False,
        download_missing = True
    ) -> Dict[str, Union[pd.DataFrame, None]]:
        '''
        Publically available method that the user can call to obtain 
        data for a list of tickers.
        '''
        #Checking validity of inputs
        assert len(tickers) > 0, 'tickers list is empty'
        assert self.__verify_vendor(vendor), f'\'{vendor}\' not in vendor list.'
        assert interval in self.__intervals.values(), f'{interval} not in given INTERVAL. Use these intervals:\n{self.__intervals}'
        assert end_datetime > start_datetime, f'start_datetime({start_datetime}) must be before end_datetime({end_datetime})'
        

        if download_missing:
            pass
        else:
            pass
    

