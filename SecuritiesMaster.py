import numpy as np
import pandas as pd
import psycopg2
import sqlalchemy
from sqlalchemy import sql
from datetime import datetime
from sql_commands import commands
from credentials import psql_credentials

class Master:
    def __init__(self, host : str, port : int, username : str, password : str, progress = False) -> None:
        self.__url = f'postgresql+psycopg2://{username}:{password}@{host}:{port}/securities_master'
        self.__engine = sqlalchemy.create_engine(self.__url, isolation_level='AUTOCOMMIT')
        self.__create_base_tables()

    def __create_base_tables(self) -> None:
        for key, command in commands.items():
            with self.__engine.connect() as conn:
                conn.execute(sql.text(command))

    #NOTE:to be worked on
    def get_data(
        self,
        ticker : str,
        interval : int,
        start_datetime : datetime,
        end_datetime : datetime,
        vendor = 'Any',
        progress = False,
        download_missing = False
    ) -> pd.DataFrame:
        assert end_datetime > start_datetime, f'start_datetime({start_datetime}) must be before end_datetime({end_datetime})' 
        pass
    
