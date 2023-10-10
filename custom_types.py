import pandas as pd


class PandasAssetData:
    __dataframe: pd.DataFrame
    __instrument: str

    def __init__(self, dataframe: pd.DataFrame, instrument: str) -> None:
        self.__dataframe = dataframe
        self.__instrument = instrument

    @property
    def dataframe(self) -> pd.DataFrame:
        return self.__dataframe

    @property
    def instrument(self) -> str:
        return self.__instrument
