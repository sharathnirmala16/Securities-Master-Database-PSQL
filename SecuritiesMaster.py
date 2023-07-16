import random
import string
import sqlalchemy
import numpy as np
import pandas as pd
from sqlalchemy import sql
from commons import INTERVAL
from datetime import datetime
from sql_commands import commands
from typing import Union, Dict, List
from credentials import psql_credentials

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
    
    @staticmethod
    def __random_string(length : int) -> str:
        letters = string.ascii_lowercase
        random_string = ''.join(random.choice(letters) for _ in range(length))
        return random_string

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

    def add_exchange(
        self, 
        abbreviation : str, 
        name : str, 
        website_url : str, 
        city : str, 
        country : str, 
        currency : str, 
        time_zone_offset : datetime
    ) -> None:
        try:
            with self.__engine.connect() as conn:
                conn.execute(sql.text(
                    f'''
                    INSERT INTO Exchange
                    (abbreviation, name, website_url, city, country, currency, time_zone_offset, created_datetime, last_updated_datetime) 
                    VALUES
                    ('{abbreviation}', '{name}', '{website_url}', '{city}', '{country}', '{currency}', '{time_zone_offset}', '{datetime.now()}', '{datetime.now()}');
                    '''
                ))
        except Exception as e:
            print(e)

    def __create_linked_table(self, linked_table_hash : str) -> None:
        '''
        Used to create the linked table which links to price table and fundamental tables
        '''
        try:
            with self.__engine.connect() as conn:
                conn.execute(sql.text(
                    f'''
                    CREATE TABLE {linked_table_hash} (
                        id SERIAL PRIMARY KEY,
                        vendor VARCHAR(255) NULL,
                        timeframe INT NOT NULL,
                        price_table VARCHAR(32) NOT NULL,
                        created_datetime TIMESTAMP NOT NULL, 
                        last_updated_datetime TIMESTAMP NOT NULL,
                        CONSTRAINT data_vendor_frk
                            FOREIGN KEY(vendor)
                                REFERENCES DataVendor(name) 
                    );
                    '''
                ))
        except Exception as e:
            print(e)

    #NOTE Delete in Final Revision, for testing purpose only
    def temp(self):
        try:
            tables = pd.read_sql_query(sql = '''select table_name from information_schema.tables where table_catalog = 'securities_master' and table_schema = 'public';''', con = self.__engine)['table_name'].to_list()
            tables.remove('datavendor')
            tables.remove('symbol')
            tables.remove('exchange')
            for table in tables:
                with self.__engine.connect() as conn:
                    conn.execute(sql.text(
                        f'''
                        DROP TABLE {table};
                        '''
                    ))

        except Exception as e:
            print(e)

    def add_symbol(
        self,
        exchange : str,
        ticker : str,
        instrument : str,
        name : str,
        sector : str,
        currency : str
    ) -> None:
        try:
            with self.__engine.connect() as conn:
                linked_table_hash = DataMaster.__random_string(32)
                conn.execute(sql.text(
                    f'''
                    INSERT INTO Symbol
                    (ticker, exchange, instrument, name, sector, currency, linked_table, created_datetime, last_updated_datetime)
                    VALUES
                    ('{ticker}', '{exchange}', '{instrument}', '{name}', '{sector}', '{currency}', '{linked_table_hash}', '{datetime.now()}', '{datetime.now()}');
                    '''
                ))
            self.__create_linked_table(linked_table_hash)
        except Exception as e:
            pass

    def get_prices(
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
    

