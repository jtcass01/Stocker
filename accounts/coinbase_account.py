#/usr/bin/env python
"""coinbase.py: """
from __future__ import annotations

__author__ = "Jacob T. Cassady"
__email__ = "jacobtaylorcassady@outlook.com"

from typing import Dict
from enum import Enum

# 3rd party modules
from coinbase.wallet.client import Client
from pandas import DataFrame
from numpy import array

# Stocker modules
from accounts.account import Account

class CoinbaseAccount(Account):

    def __init__(self, deposit_history: DataFrame, transaction_history: DataFrame, api_key: str, api_secret: str):
        self.interface: Client = CoinbaseAccount.Interface(api_key=api_key, api_secret=api_secret)
        self.transaction_history: DataFrame = transaction_history
        self.total_deposit: float = deposit_history['Amount'].sum()

    def analyze_investment(self, symbol) -> Dict[str, float]:
        """[summary]

        Args:
            symbol ([type]): [description]

        Returns:
            Dict[str, float]: {'investment': 3786.771289, 'return': 1762.070422, 'fees': 5.865150065}
        """
        total_investment: float = 0.
        total_return: float = 0.
        total_fees: float = 0.
        relevant_df = self.transaction_history[self.transaction_history.Asset == symbol]
        unique_transaction_types: array = relevant_df['Transaction Type'].unique()

        for transaction_type in unique_transaction_types:
            relevant_df = relevant_df[relevant_df['Transaction Type'] == transaction_type]
            transaction_type: CoinbaseAccount.TRANSACTION_TYPE = CoinbaseAccount.TRANSACTION_TYPE(transaction_type)
            transaction_analysis: Dict[str, float] = transaction_type.analyze(transaction_history=self.transaction_history, symbol=symbol)
            total_investment += transaction_analysis['investment']
            total_return += transaction_analysis['return']
            total_fees += transaction_analysis['fees']

        return {
            "investment": total_investment,
            "return": total_return,
            "fees": total_fees
        }

    class Interface(Client):
        def __init__(self, api_key: str, api_secret: str):
            Client.__init__(self, api_key=api_key, api_secret=api_secret)

    class TRANSACTION_TYPE(Enum):
        BUY = "Buy"
        SEND = "Send"
        CONVERT = "Convert"
        COINBASE_EARN = "Coinbase Earn"
        REWARDS_INCOME = "Rewards Income"

        def analyze(self, transaction_history: DataFrame, symbol: str) -> Dict[str, float]:
            transaction_investment: float = 0.
            transaction_fees: float = 0.
            transaction_return: float = 0.

            if self == CoinbaseAccount.TRANSACTION_TYPE.BUY:
                relevant_df = transaction_history[(transaction_history.Asset == symbol) & (transaction_history['Transaction Type'] == self.value)]
                transaction_investment = relevant_df['USD Subtotal'].sum()
                transaction_fees = relevant_df['USD Fees'].sum()
            elif self == CoinbaseAccount.TRANSACTION_TYPE.SEND:
                pass
            elif self == CoinbaseAccount.TRANSACTION_TYPE.CONVERT:
                conversions_from_df = transaction_history[(transaction_history.Asset == symbol) & (transaction_history['Transaction Type'] == self.value)]
                transaction_return = conversions_from_df['USD Subtotal'].sum()
                transaction_fees = conversions_from_df['USD Fees'].sum()

                conversions_to_df = transaction_history[(transaction_history.Asset != symbol) & (transaction_history['Transaction Type'] == self.value)]
                conversions_to_df = conversions_to_df[transaction_history.Notes.str.contains(symbol)]
                transaction_investment = conversions_to_df['USD Subtotal'].sum()
                transaction_fees = conversions_to_df['USD Fees'].sum() + transaction_fees
            elif self == CoinbaseAccount.TRANSACTION_TYPE.COINBASE_EARN:
                relevant_df = transaction_history[(transaction_history.Asset == symbol) & (transaction_history['Transaction Type'] == self.value)]
                transaction_return = relevant_df['USD Subtotal'].sum()
            elif self == CoinbaseAccount.TRANSACTION_TYPE.REWARDS_INCOME:
                relevant_df = transaction_history[(transaction_history.Asset == symbol) & (transaction_history['Transaction Type'] == self.value)]
                transaction_return = relevant_df['USD Subtotal'].sum()

            return {
                "investment": transaction_investment,
                "return": transaction_return,
                "fees": transaction_fees
            }
