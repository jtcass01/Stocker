#/usr/bin/env python
"""binance.py: """
from __future__ import annotations

__author__ = "Jacob T. Cassady"
__email__ = "jacobtaylorcassady@outlook.com"

from typing import Dict

# 3rd party modules
from binance.client import Client
from pandas import DataFrame
from numpy import array

# Stocker modules
from accounts.account import Account

class BinanceAccount(Account):
    """[summary]"""

    def __init__(self, deposit_history: DataFrame, transaction_history: DataFrame, api_key: str, api_secret: str):
        """Constructor.

        Args:
            transaction_history (DataFrame): [description]
            api_key (str): [description]
            api_secret (str): [description]"""
        self.transaction_history = transaction_history
        self.interface: Client = BinanceAccount.Interface(api_key=api_key,
                                                          api_secret=api_secret)
        self.total_deposit: float = deposit_history['Amount'].sum()

    def analyze_investment(self, symbol) -> Dict[str, float]:
        relevant_df = self.transaction_history[self.transaction_history.Pair == symbol]

        purchases = relevant_df[relevant_df.Type == "BUY"]
        sales = relevant_df[relevant_df.Type == "SELL"]

        investment_analysis: Dict[str, float] = self.sum_transactions(transactions=purchases)
        return_analysis: Dict[str, float] = self.sum_transactions(transactions=sales)

        total_fees = investment_analysis['total_fee'] + return_analysis['total_fee']

        return {
            "investment": investment_analysis['value'],
            "return": return_analysis['value'],
            'fees': total_fees
        }

    def sum_transactions(self, transactions: DataFrame) -> Dict[str, float]:
        """[summary]

        Args:
            transactions (DataFrame): [description]

        Returns:
            Dict[str, float]: [description]"""
        transaction_analysis: Dict[str, float] = {}
        transaction_analysis['value'] = transactions['Total'].sum()
        fee_currencies: array = transactions['Fee Currency'].unique()
        ticker_data = self.interface.get_all_tickers()

        total_fee = 0.
        for fee_currency in fee_currencies:
            if fee_currency != "USD":
                fee_symbol = fee_currency + "USD"
                fee_exchange_rate = [float(price_entry['price']) for price_entry in ticker_data if price_entry['symbol'] == fee_symbol][0]
            else:
                fee_exchange_rate = 1.

            fee: float = transactions[transactions['Fee Currency'] == fee_currency]['Fee'].sum() * fee_exchange_rate

            transaction_analysis[fee_currency + "_fee"] = fee
            total_fee += fee
        transaction_analysis["total_fee"] = total_fee

        return transaction_analysis

    class Interface(Client):
        def __init__(self, api_key: str, api_secret: str):
            """[summary]

            Args:
                api_key (str): [description]
                api_secret (str): [description]"""
            Client.__init__(self, api_key=api_key, api_secret=api_secret, tld="us")

        def get_prices(self, symbols: list) -> dict:
            """[summary]

            Args:
                symbols (list): [description]

            Returns:
                dict: [description]"""
            price_list = self.get_all_tickers()
            prices = {}

            for symbol in symbols:
                prices[symbol] = [float(price_entry['price']) for price_entry in price_list if price_entry['symbol'] == symbol][0]

            return prices
