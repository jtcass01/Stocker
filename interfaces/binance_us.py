#/usr/bin/env python
"""binance.py: """
from __future__ import annotations

__author__ = "Jacob T. Cassady"
__email__ = "jacobtaylorcassady@outlook.com"

# Built-in modules
from typing import Dict

# 3rd party modules
from binance.client import Client

class BinanceInterface(object):
    def __init__(self, api_key: str, api_secret: str):
        """[summary]

        Args:
            api_key (str): [description]
            api_secret (str): [description]"""
        self.client = Client(api_key=api_key, api_secret=api_secret)

    def get_prices(self, symbols: list) -> dict:
        """[summary]

        Args:
            symbols (list): [description]

        Returns:
            dict: [description]"""
        price_list = self.client.get_all_tickers()
        prices = {}

        for symbol in symbols:
            prices[symbol] = [float(price_entry['price']) for price_entry in price_list if price_entry['symbol'] == symbol][0]

        return prices
