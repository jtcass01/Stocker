#/usr/bin/env python
"""holdings.py:"""
from __future__ import annotations

__author__ = "Jacob T. Cassady"
__email__ = "jacobtaylorcassady@outlook.com"

from utilities.Logger import Logger

# Built-in Modules
from typing import Dict, Union, Callable
from abc import ABC, abstractclassmethod
from enum import Enum, unique

# Stocker Library Modules
from interfaces.stock import get_stock_price
from utilities.Logger import Logger

class Holdings(object):
    """[summary]"""
    def __init__(self, stocker: object, 
                 cryptocoins: Dict[str, Holdings.Cryptocoin], 
                 stocks: Dict[str, Holdings.Stock],
                 checking_accounts: Dict[str, Holdings.CheckingAccount],
                 floating_usd: Dict[str, Holdings.FloatingUSD] = None):
        """Constructor.

        Args:
            cryptocoins (Dict[str, Holdings.Cryptocoin]): [description]
            stocks (Dict[str, Holdings.Stock]): [description]
            checking_accounts (Dict[str, Holdings.CheckingAccount]): [description]"""
        self.stocker: object = stocker
        self.cryptocoins: Dict[str, Holdings.Cryptocoin] = cryptocoins
        self.stocks: Dict[str, Holdings.Stock] = stocks
        self.checking_accounts: Dict[str, Holdings.CheckingAccount] = checking_accounts
        self.floating_usd = floating_usd

    def update(self) -> None:
        """[summary]"""
        if self.stocker.verbose:
            Logger.console_log(message=str(type(self)) + " is updating...",
                               message_type=Logger.MESSAGE_TYPE.STATUS)

        coin_prices: Dict[str, float] = self.stocker.binance_interface.get_prices(symbols=list(self.cryptocoins.keys()))
        for coin_symbol, coin in self.cryptocoins.items():
            coin.price = coin_prices[coin_symbol]
            #coin.float = self.stocker.binance_interface.client.get_asset_balance(asset=coin_symbol)
            if self.stocker.verbose:
                Logger.console_log(message="[CRYPTO] " + coin.name + " is currently valued at $" + str(coin.price) + " per coin.",
                                   message_type=Logger.MESSAGE_TYPE.STATUS)
        for stock_symbol, stock in self.stocks.items():
            stock.price = get_stock_price(symbol=stock_symbol)
            if self.stocker.verbose:
                Logger.console_log(message="[STOCK] " + stock.name + " is currently valued at $" + str(stock.price) + " per share.",
                                   message_type=Logger.MESSAGE_TYPE.STATUS)
        for account_name, checking_account in self.checking_accounts.items():
            #checking_account.update()
            if self.stocker.verbose:
                Logger.console_log(message="[CHECKING] " + account_name + " is currently valued at $" + str(checking_account.equity),
                                   message_type=Logger.MESSAGE_TYPE.STATUS)

        if self.stocker.verbose:
            Logger.console_log(message=str(type(self)) + " is finished updating.",
                               message_type=Logger.MESSAGE_TYPE.SUCCESS)

    def calculate_equity(self, holding_type: Union[str, Holdings.HOLDING_TYPE] = "all") -> float:
        """[summary]

        Args:
            holding_type (Union[str, Holdings.HOLDING_TYPE], optional): [description]. Defaults to "all".

        Returns:
            float: [description]"""
        assert type(holding_type) == str or type(holding_type) == Holdings.HOLDING_TYPE

        if self.stocker.verbose:
            Logger.console_log(message=str(type(self)) + " is calculating the equity of holding_type: " + str(holding_type),
                               message_type=Logger.MESSAGE_TYPE.STATUS)

        equity: float = 0.

        if type(holding_type) == str:
            holding_type: Holdings.HOLDING_TYPE = Holdings.HOLDING_TYPE(holding_type)

        if holding_type == Holdings.HOLDING_TYPE.STOCK or holding_type == Holdings.HOLDING_TYPE.ALL:
            equity += Holdings.calculate_holding_equity(holdings=self.stocks, verbose=self.stocker.verbose)
        if holding_type == Holdings.HOLDING_TYPE.CRYPTOCURRENCY or holding_type == Holdings.HOLDING_TYPE.ALL:
            equity += Holdings.calculate_holding_equity(holdings=self.cryptocoins, verbose=self.stocker.verbose)
        if holding_type == Holdings.HOLDING_TYPE.CHECKING or holding_type == Holdings.HOLDING_TYPE.ALL:
            equity += Holdings.calculate_holding_equity(holdings=self.checking_accounts, verbose=self.stocker.verbose)
        if (holding_type == Holdings.HOLDING_TYPE.FLOATING_USD or holding_type == Holdings.HOLDING_TYPE.ALL) and self.floating_usd is not None:
            equity += Holdings.calculate_holding_equity(holdings=self.floating_usd, verbose=self.stocker.verbose)

        if self.stocker.verbose:
            Logger.console_log(message=str(type(self)) + " equity of holding_type: " + str(holding_type) + " = " + "$%.2f" % equity,
                               message_type=Logger.MESSAGE_TYPE.SUCCESS)

        return equity

    @staticmethod
    def calculate_holding_equity(holdings: Union[Dict[str, Holdings.Stock], 
                                                 Dict[str, Holdings.Cryptocoin], 
                                                 Dict[str, Holdings.CheckingAccount],
                                                 Dict[str, Holdings.FloatingUSD]],
                                 verbose: bool = False) -> float:
        """[summary]

        Args:
            holdings (Union[Dict[str, Holdings.Stock], Dict[str, Holdings.Cryptocoin], Dict[str, Holdings.CheckingAccount], Dict[str, Holdings.FloatingUSD]]): [description]
            verbose (bool, optional): [description]. Defaults to False.

        Returns:
            float: [description]"""
        total_equity: float = 0.
        if len(holdings.keys()) > 0:
            equity_type: Callable = type(holdings[list(holdings.keys())[0]])
        else:
            return 0.

        for holding_name, holding in holdings.items():
            holding_equity = holding.calculate_equity()
            total_equity += holding_equity
            if verbose:
                Logger.console_log(message=str(holding) + " has a " + str(equity_type) + " value of " + "$%.2f" % holding_equity,
                                   message_type=Logger.MESSAGE_TYPE.STATUS)

        if verbose:
            Logger.console_log(message=str(Holdings) + " has calculated a total " + str(equity_type) + " equity of " + "$%.2f" % total_equity,
                               message_type=Logger.MESSAGE_TYPE.SUCCESS)

        return total_equity

    class Holding(ABC, object):
        """[summary]"""
        @abstractclassmethod
        def calculate_equity(self) -> float:
            """TODO"""
            pass

        @abstractclassmethod
        def __str__(self) -> str:
            pass

    class Cryptocoin(Holding):
        """[summary]"""
        def __init__(self, symbol: str, name: str, coin: str, quantity: float):
            """Constructor.

            Args:
                symbol (str): [description]
                name (str): [description]
                coin (str): [description]
                quantity (float): [description]"""
            self.symbol = symbol
            self.name = name
            self.coin = coin
            self.quantity = quantity
            self.float = None
            self.price = None

        def calculate_equity(self) -> float:
            """[summary]

            Returns:
                float: [description]"""
            assert self.price is not None, "Equity cannot be calculated without initially updating price."
            return self.quantity * self.price

        def __str__(self) -> str:
            """[summary]

            Returns:
                str: [description]"""
            return self.name

    class Stock(Holding):
        """[summary]"""
        def __init__(self, symbol: str, name: str, 
                     quantity: float, cost_basis_per_share: float):
            """Constructor.

            Args:
                symbol (str): [description]
                name (str): [description]
                quantity (float): [description]
                cost_basis_per_share (float): [description]"""
            self.symbol = symbol
            self.name = name
            self.quantity = quantity
            self.cost_basis_per_share = cost_basis_per_share
            self.price: Union[float, None] = None
            self.equity: Union[float, None] = None

        def calculate_equity(self) -> float:
            """[summary]

            Returns:
                float: [description]"""
            assert self.price is not None, "Equity cannot be calculated without initially updating price."
            return self.quantity * self.price

        def __str__(self) -> str:
            """[summary]

            Returns:
                str: [description]"""
            return self.name

    class CheckingAccount(Holding):
        """[summary]"""
        def __init__(self, name: str, equity: float):
            """Constructor.

            Args:
                name (str): [description]
                balance (float): [description]"""
            self.name = name
            self.equity = equity

        def calculate_equity(self) -> float:
            """[summary]

            Returns:
                float: [description]"""
            return self.equity

        def update(self, stocker: object) -> None:
            """[summary]

            Args:
                stocker (object): [description]"""
            mint_accounts_data = stocker.mint.get_accounts()

            matching_account_data = [account_data for account_data in mint_accounts_data if account_data['accountName'] == self.name]

            assert len(matching_account_data) == 1, "An unexpected number of matching account data was found: " + str(len(matching_account_data))

            self.equity = matching_account_data[0]['amount']

        def __str__(self) -> str:
            """[summary]

            Returns:
                str: [description]"""
            return self.name

    class FloatingUSD(Holding):
        """[summary]"""
        def __init__(self, location: Holdings.FloatingUSD.FLOAT_LOCATION, equity: float):
            self.location = location
            self.equity = equity

        def calculate_equity(self) -> float:
            return self.equity

        @unique
        class FLOAT_LOCATION(Enum):
            BINANCE_US = "binance.us"

            def retrieve_float(self, stocker: object) -> Holdings.FloatingUSD:
                """[summary]

                Args:
                    stocker (object): [description]

                Returns:
                    float: [description]"""
                if self == Holdings.FloatingUSD.FLOAT_LOCATION.BINANCE_US:
                    return Holdings.FloatingUSD(location=self.value, 
                                                equity=stocker.binance_interface.client.get_asset_balance(asset="USD"))

    @unique
    class HOLDING_TYPE(Enum):
        ALL = "all"
        STOCK = "stock"
        CRYPTOCURRENCY = "crypto"
        CHECKING = "checking account"
        FLOATING_USD = "float"
