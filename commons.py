from enum import Enum


class VENDOR(Enum):
    YAHOO = "Yahoo Finance"
    ICICI = "ICICI Direct Breeze API"
    ANGELBROKING = "Angel Broking Smart API"


class EXCHANGE(Enum):
    NSE = "National Stock Exchange"
    BSE = "Bombay Stock Exchange"


class INSTRUMENT(Enum):
    STOCK = "Stock"
    ETF = "Exchange Traded Fund"
    MF = "Mutual Fund"
    FUTURE = "Future"
    OPTION = "Option"
    FOREX = "Foreign Exchange"
    CRYPTO = "Cryptocurrency"


class INTERVAL(Enum):
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


class NSE_URL(Enum):
    ALL_TICKERS = "https://nsearchives.nseindia.com/content/equities/EQUITY_L.csv"
    NIFTY50 = "https://archives.nseindia.com/content/indices/ind_nifty50list.csv"
    NIFTY100 = "https://www.niftyindices.com/IndexConstituent/ind_nifty100list.csv"
    NIFTY500 = "https://archives.nseindia.com/content/indices/ind_nifty500list.csv"
    NIFTYMIDCAP150 = (
        "https://www.niftyindices.com/IndexConstituent/ind_niftymidcap150list.csv"
    )
    NIFTYSMALLCAP250 = (
        "https://www.niftyindices.com/IndexConstituent/ind_niftysmallcap250list.csv"
    )
    NIFTYMICROCAP250 = (
        "https://www.niftyindices.com/IndexConstituent/ind_niftymicrocap250_list.csv"
    )
    NIFTYNEXT50 = (
        "https://archives.nseindia.com/content/indices/ind_niftynext50list.csv"
    )
    NIFTYBANK = "https://www.niftyindices.com/IndexConstituent/ind_niftybanklist.csv"
    NIFTYIT = "https://www.niftyindices.com/IndexConstituent/ind_niftyitlist.csv"
    NIFTYHEALTHCARE = (
        "https://www.niftyindices.com/IndexConstituent/ind_niftyhealthcarelist.csv"
    )
    NIFTYFINSERVICE = (
        "https://www.niftyindices.com/IndexConstituent/ind_niftyfinancelist.csv"
    )
    NIFTYAUTO = "https://www.niftyindices.com/IndexConstituent/ind_niftyautolist.csv"
    NIFTYPHARMA = (
        "https://www.niftyindices.com/IndexConstituent/ind_niftypharmalist.csv"
    )
    NIFTYFMCG = "https://www.niftyindices.com/IndexConstituent/ind_niftyfmcglist.csv"
    NIFTYMEDIA = "https://www.niftyindices.com/IndexConstituent/ind_niftymedialist.csv"
    NIFTYMETAL = "https://www.niftyindices.com/IndexConstituent/ind_niftymetallist.csv"
    NIFTYREALTY = (
        "https://www.niftyindices.com/IndexConstituent/ind_niftyrealtylist.csv"
    )
