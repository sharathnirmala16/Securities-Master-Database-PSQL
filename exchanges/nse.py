import pandas as pd

from common.enums import NSE_URLS
from common.exceptions import IndexNotFoundException
from requests import Session
from exchanges.exchange import Exchange
from io import StringIO


class Nse(Exchange):
    __abbreviation = "NSE"

    def __init__(self) -> None:
        super().__init__()

    @property
    def abbreviation(self) -> str:
        return self.__abbreviation

    def get_tickers(self, index: str) -> pd.DataFrame:
        if index not in NSE_URLS._member_names_:
            raise IndexNotFoundException(
                f"{index} is either not supported yet or invalid."
            )

        try:
            session = Session()
            # Emulate browser
            session.headers.update(
                {
                    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.61 Safari/537.36"
                }
            )
            # Get the cookies from the main page (will update automatically in headers)
            session.get("https://www.nseindia.com/")
            # Get the API data
            data = session.get(NSE_URLS[index].value).text
            data = StringIO(data)
            df = pd.read_csv(data, sep=",")
            return df
        except Exception as e:
            raise e
