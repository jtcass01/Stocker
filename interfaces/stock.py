from time import sleep

from pandas import DataFrame
from yahoo_fin.stock_info import get_live_price, get_data
from StatusLogger import Logger, Message

def get_stock_price(symbol: str) -> float:
    """[summary]

    Args:
        symbol (str): [description]

    Returns:
        DataFrame: [description]"""
    try:
        price: float = get_live_price(symbol)
        return price
    except Exception as error:
        Logger.console_log(message="Exception {} encountered when attempting to get price for symbol {}. Sleeping and trying again.".format(error, symbol),
                           message_type=Message.MESSAGE_TYPE.MINOR_FAIL)
        sleep(120)
        return get_stock_price(symbol=symbol)
        

def get_stock_data(symbol: str) -> DataFrame:
    """[summary]

    Args:
        symbol (str): [description]

    Returns:
        DataFrame: [description]"""
    stock_data: DataFrame = get_data(symbol)
    stock_data = stock_data.drop('ticker', axis=1)
    return stock_data

if __name__ == "__main__":
    print(get_stock_price(symbol="GME"))
