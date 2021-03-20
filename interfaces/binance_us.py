#/usr/bin/env python
"""binance.py: """
from __future__ import annotations

__author__ = "Jacob T. Cassady"
__email__ = "jacobtaylorcassady@outlook.com"

# Built-in modules
from unittest import main, TestCase

# 3rd party modules
from binance.client import Client

class BinanceInterface(object):
    def __init__(self, api_key: str, api_secret: str):
        self.client = Client(api_key=api_key, api_secret=api_secret)

class Test_BinanceInterface(TestCase):
    def test_initialization(self):
        """[summary]"""
        print("Starting test: Test_BinanceInterface.test_initialization")
        test_binance_interface: BinanceInterface = BinanceInterface(api_key="", api_secret="")
        print("Test complete.")

if __name__ == "__main__":
    main()
