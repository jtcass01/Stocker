#/usr/bin/env python
"""stocker.py:"""

__author__ = "Jacob T. Cassady"
__email__ = "jacobtaylorcassady@outlook.com"

from typing import Union
from time import sleep

from cryptocompare import get_price
from StatusLogger import Logger, Message

from accounts.binance_us_account import BinanceAccount
from accounts.coinbase_account import CoinbaseAccount

def get_crypto_price(coin_name: str, binance_account: Union[None, BinanceAccount] = None, 
                     coinbase_account: Union[None, CoinbaseAccount] = None) -> float:
    """[summary]

    Args:
        coin_name (str): [description]
        binance_account (Union[None, BinanceAccount], optional): [description]. Defaults to None.
        coinbase_account (Union[None, CoinbaseAccount], optional): [description]. Defaults to None.

    Returns:
        float: [description]"""
    try:
        return get_price(coin_name, "USD")[coin_name]["USD"]
    except Exception as error:
        Logger.console_log(message=f"Exception {error} found when attempting to get price from cryptocompare.",
                            message_type=Message.MESSAGE_TYPE.MINOR_FAIL)

    if binance_account is not None:
        try:
            return float(binance_account.interface.get_ticker(symbol=coin_name+"USD")['lastPrice'])
        except Exception as error:
            Logger.console_log(message=f"Exception {error} found when attempting to get price from binance.",
                                message_type=Message.MESSAGE_TYPE.MINOR_FAIL)

    if coinbase_account is not None:
        try:
            return float(coinbase_account.interface.get_buy_price(currency_pair=coin_name+"-USD")['amount'])
        except Exception as error:
            Logger.console_log(message=f"Exception {error} found when attempting to get price from coinbase.",
                            message_type=Message.MESSAGE_TYPE.MINOR_FAIL)

    sleep(5 * 60)
    return get_crypto_price(coin_name=coin_name, binance_account=binance_account, coinbase_account=coinbase_account)
