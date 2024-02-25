from abc import ABC, abstractmethod


class Exchange(ABC):
    @abstractmethod
    def get_tickers(self, index: str) -> dict[str, str]:
        pass

    @property
    @abstractmethod
    def abbreviation(self) -> str:
        pass
