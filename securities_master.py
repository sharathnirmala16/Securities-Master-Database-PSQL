import random
import string
import importlib
import sqlalchemy
import numpy as np
import pandas as pd


from sqlalchemy import sql, exc
from datetime import datetime
from sql_commands import commands
from typing import Union, Dict, List
from credentials import psql_credentials
from custom_types import PandasAssetData
from Exchanges.index_loader import IndexLoader
from commons import INTERVAL, VENDOR, EXCHANGE
from VendorsApiManagers.api_manager import APIManager


class SecuritiesMaster:
    """
    User can create an instance of this class to obtain data
    """

    def __init__(
        self, host: str, port: int, username: str, password: str, progress=False
    ) -> None:
        """
        Creates the necessary database connection objects.
        """
        try:
            self.__url = f"postgresql+psycopg2://{username}:{password}@{host}:{port}/securities_master"
            self.__engine = sqlalchemy.create_engine(
                self.__url, isolation_level="AUTOCOMMIT"
            )
            self.__create_base_tables()
        except Exception as e:
            raise e

    def __create_base_tables(self) -> None:
        """
        Specifically for creating the base tables that are
        necessary for basic operations.
        """
        try:
            for command in commands.values():
                with self.__engine.connect() as conn:
                    conn.execute(sql.text(command))
        except Exception as e:
            raise e

    # NOTE Delete in Final Revision, for testing purpose only
    def temp(self):
        try:
            return self.__get_table_object("symbol")
        except Exception as e:
            raise e

    def get_all_tables(self) -> List[str]:
        try:
            tables = pd.read_sql_query(
                sql="""select table_name from information_schema.tables where table_catalog = 'securities_master' and table_schema = 'public';""",
                con=self.__engine,
            )["table_name"].to_list()
            try:
                tables.remove("users")
                tables.remove("token")
            except:
                pass
            return tables
        except Exception as e:
            raise e

    def get_table(self, table_name: str) -> pd.DataFrame:
        try:
            table = pd.read_sql_table(table_name=table_name, con=self.__engine)
            return table
        except Exception as e:
            raise e

    @staticmethod
    def __get_column_names(table: sqlalchemy.Table) -> List[str]:
        columns_list = []
        for column in table.columns:
            columns_list.append(column.name)

        return columns_list

    def __get_table_object(self, table_name: str) -> sqlalchemy.Table:
        return sqlalchemy.Table(
            table_name, sqlalchemy.MetaData(bind=self.__engine), autoload=True
        )

    def add_row(self, table_name: str, row_data: dict) -> None:
        try:
            table = self.__get_table_object(table_name)
            if "created_datetime" in self.__get_column_names(table):
                row_data["created_datetime"] = datetime.now()
            if "last_updated_datetime" in self.__get_column_names(table):
                row_data["last_updated_datetime"] = datetime.now()
            stmt = sqlalchemy.insert(table).values(row_data)
            with self.__engine.connect() as conn:
                conn.execute(stmt)
        except Exception as e:
            raise e

    def edit_row(
        self,
        table_name: str,
        old_row_data: Dict[str, str],
        new_row_data: Dict[str, str],
    ) -> None:
        try:
            table = self.__get_table_object(table_name)
            if "created_datetime" in self.__get_column_names(table):
                new_row_data.pop("created_datetime")
            if "last_updated_datetime" in self.__get_column_names(table):
                new_row_data["last_updated_datetime"] = datetime.now()
            primary_key_values = dict(
                map(lambda col: (col.name, old_row_data[col.name]), table.primary_key)
            )

            stmt = (
                sqlalchemy.update(table)
                .values(new_row_data)
                .where(
                    sqlalchemy.and_(
                        *(
                            getattr(table.c, key) == primary_key_values[key]
                            for key in primary_key_values
                        )
                    )
                )
            )
            with self.__engine.connect() as conn:
                conn.execute(stmt)
        except Exception as e:
            raise e

    def delete_row(self, table_name: str, row_data: Dict[str, str]) -> None:
        try:
            table = self.__get_table_object(table_name)
            primary_key_values = dict(
                map(lambda col: (col.name, row_data[col.name]), table.primary_key)
            )
            stmt = sqlalchemy.delete(table).where(
                sqlalchemy.and_(
                    *(
                        getattr(table.c, key) == primary_key_values[key]
                        for key in primary_key_values
                    )
                )
            )
            with self.__engine.connect() as conn:
                conn.execute(stmt)
        except Exception as e:
            raise e

    def delete_table(self, table_name: str) -> None:
        try:
            table = self.__get_table_object(table_name)
            table.drop()
        except Exception as e:
            raise e

    def __verify_vendor(self, vendor: str) -> bool:
        vendors = self.get_table("datavendor")["name"].to_list()
        if vendor in vendors:
            return True
        return False

    def __verify_exchange(self, exchange: str) -> bool:
        exchanges = self.get_table("exchange")["name"].to_list()
        if exchange in exchanges:
            return True
        return False

    def get_prices(
        self,
        interval: int,
        start_datetime: datetime,
        end_datetime: datetime,
        vendor: str,
        exchange: str,
        tickers: List[str] = None,
        index: str = None,
        vendor_login_credentials: Dict[str, str] = {},
        progress=False,
    ) -> Dict[str, pd.DataFrame]:
        """
        Publically available method that the user can call to obtain
        data for a list of tickers.
        """
        # Checking validity of inputs
        if len(tickers) < 0:
            raise Exception("tickers list is empty")
        if not self.__verify_vendor(vendor):
            raise Exception(f"'{vendor}' not in vendor list.")
        if not self.__verify_exchange(exchange):
            raise Exception(f"'{exchange}' not in vendor list.")
        if interval not in [interval.value for interval in INTERVAL]:
            raise Exception(f"{interval} not in INTERVAL Enum.")
        if end_datetime < start_datetime:
            raise Exception(
                f"start_datetime({start_datetime}) must be before end_datetime({end_datetime})"
            )

        vendor_obj: APIManager = getattr(
            importlib.import_module(
                name=f"VendorsApiManagers.{VENDOR(vendor).name.lower()}"
            ),  # module name
            f"{VENDOR(vendor).name[0:1] + VENDOR(vendor).name[1:].lower()}Data",  # class name
        )(vendor_login_credentials)

        if tickers is None and index is None:
            raise Exception("Either 'tickers' of 'index' must be given")
        if index is not None and tickers is None:
            exchange_obj: IndexLoader = getattr(
                importlib.import_module(
                    name=f"Exchanges.{EXCHANGE(exchange).name.lower()}_tickers"
                ),  # module name
                f"{EXCHANGE(exchange).name}Tickers",  # class name
            )
            tickers = list(exchange_obj.get_tickers(index=index).keys())

        data_dict: Dict[str, pd.DataFrame] = {}
        # load data from the database, if not found or valid range is not present, then get them from the vendor
        for ticker in tickers:
            table_name: str = (
                f"PRICES_{ticker}_{EXCHANGE(exchange).name}_{INTERVAL(interval).name}"
            )
            try:
                data: pd.DataFrame = pd.read_sql_query(
                    sql=f"""
                        SELECT * FROM {table_name} 
                        WHERE 
                            datetime >= '{start_datetime.strftime("%Y-%m-%d %H:%M:%S.%f")}' 
                            AND 
                            datetime <= '{end_datetime.strftime("%Y-%m-%d %H:%M:%S.%f")}'
                    """,
                    con=self.__engine,
                )
                if data.empty:
                    raise ValueError
            except ValueError and exc.ProgrammingError:
                data = vendor_obj.get_data(
                    interval=interval,
                    exchange=exchange,
                    start_datetime=start_datetime,
                    end_datetime=end_datetime,
                    tickers=[ticker],
                    replace_close=False,
                    progress=False,
                )

            data_dict[ticker] = data[ticker]

        return data_dict
