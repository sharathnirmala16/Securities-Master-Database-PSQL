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

            # Converts the INTERVAL class into a dictionary for reference inside the DataMaster class.
            self.__intervals = {
                v: m
                for v, m in vars(INTERVAL).items()
                if not (v.startswith("_") or callable(m))
            }
        except Exception as e:
            print(e)

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
            print(e)

    # NOTE Delete in Final Revision, for testing purpose only
    def temp(self):
        try:
            return self.__get_column_names(self.__get_table_object("datavendor"))
        except Exception as e:
            print(e)

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
            print(e)

    def get_table(self, table_name: str) -> pd.DataFrame:
        try:
            table = pd.read_sql_table(table_name=table_name, con=self.__engine)
            return table
        except Exception as e:
            print(e)

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
            print(e)

    # def edit_row(self,table_name: str, row_data: dict):
    #     try:
    #         table = self.__get_table_object(table_name)
    #         stmt = sqlalchemy.update(table).values(row_data).where(table.c.primary_key_column == primary_key_value)

    #     except Exception as e:
    #         print(e)

    def delete_table(self, table_name: str) -> None:
        try:
            table = self.__get_table_object(table_name)
            table.drop()
        except Exception as e:
            print(e)

    def get_prices(
        self,
        tickers: List[str],
        interval: int,
        start_datetime: datetime,
        end_datetime: datetime,
        vendor="Any",
        progress=False,
        download_missing=True,
    ) -> Dict[str, Union[pd.DataFrame, None]]:
        """
        Publically available method that the user can call to obtain
        data for a list of tickers.
        """
        # Checking validity of inputs
        assert len(tickers) > 0, "tickers list is empty"
        assert self.__verify_vendor(vendor), f"'{vendor}' not in vendor list."
        assert (
            interval in self.__intervals.values()
        ), f"{interval} not in given INTERVAL. Use these intervals:\n{self.__intervals}"
        assert (
            end_datetime > start_datetime
        ), f"start_datetime({start_datetime}) must be before end_datetime({end_datetime})"

        if download_missing:
            pass
        else:
            pass
