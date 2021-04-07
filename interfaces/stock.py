from pandas import DataFrame
from yahoo_fin.stock_info import get_live_price, get_data

def get_stock_price(symbol: str) -> float:
    """[summary]

    Args:
        symbol (str): [description]

    Returns:
        DataFrame: [description]"""
    return get_live_price(symbol)

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
