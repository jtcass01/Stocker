#/usr/bin/env python
"""holdings.py:"""
from __future__ import annotations

__author__ = "Jacob T. Cassady"
__email__ = "jacobtaylorcassady@outlook.com"

# Built-in Modules
from typing import Dict, Union, Callable, List, TextIO, Any
from abc import ABC, abstractclassmethod, abstractstaticmethod
from enum import Enum, unique
from threading import Lock
from time import time

# 3rd party modules
from pandas import DataFrame, Series
from numpy import array
from StatusLogger import Logger, Message

# Stocker Library Modules
from interfaces.stock import get_stock_price
from interfaces.crypto import get_crypto_price
from interfaces.mint import Mint
from accounts.binance_us_account import BinanceAccount
from accounts.coinbase_account import CoinbaseAccount
from utilities.time_util import Stocker_Event
from utilities.Cipher import VigenereCipher, load_json_resource

class Holdings(object):
    """[summary]"""
    def __init__(self, cryptocoins: Dict[str, Holdings.Cryptocoin], 
                 stocks: Dict[str, Holdings.Stock],
                 checking_accounts: Dict[str, Holdings.CheckingAccount],
                 floating_usd: Dict[str, float]):
        """[summary]

        Args:
            stocker (object): [description]
            cryptocoins (Dict[str, Holdings.Cryptocoin]): [description]
            stocks (Dict[str, Holdings.Stock]): [description]
            checking_accounts (Dict[str, Holdings.CheckingAccount]): [description]
            floating_usd (Dict[str, float]): [description]"""
        self.lock: Lock = Lock()
        self.initial_update = Stocker_Event()

        self.cryptocoins: Dict[str, Holdings.Cryptocoin] = cryptocoins
        self.crypto_df: DataFrame = DataFrame(columns=Holdings.Cryptocoin.get_columns())
        self.crypto_df.set_index("datetime")

        self.stocks: Dict[str, Holdings.Stock] = stocks
        self.stocks_df: DataFrame = DataFrame(columns=Holdings.Stock.get_columns())
        self.stocks_df.set_index("datetime")

        self.checking_accounts: Dict[str, Holdings.CheckingAccount] = checking_accounts
        self.checking_account_df: DataFrame = DataFrame(columns=Holdings.CheckingAccount.get_columns())
        self.checking_account_df.set_index("datetime")

        self.floating_usd: Dict[str, float] = floating_usd
        self.floating_usd_df: DataFrame = DataFrame(columns=["datetime", "location", "equity"])
        self.floating_usd_df.set_index("datetime")

    def __str__(self) -> str:
        return str({
            "stocks": [{"symbol": stock_name, "equity": stock.calculate_equity()} for stock_name, stock in self.stocks.items()],
            "crypto": [{"symbol": crypto_name, "equity": crypto.calculate_equity()} for crypto_name, crypto in self.cryptocoins.items()],
            "checking": [{"account name": account_name, "equity": checking_account.equity} for account_name, checking_account in self.checking_accounts.items()],
            "float": [{"location": location, "equity": equity} for location, equity in self.floating_usd.items()]
        })

    def update(self, binance_account: Union[BinanceAccount, None] = None, coinbase_account: Union[CoinbaseAccount, None] = None,
               verbose: bool = False) -> None:
        """[summary]"""
        update_time = time()

        self.lock.acquire()
        for coin_name, coin in self.cryptocoins.items():
            coin.price = get_crypto_price(coin_name=coin_name, binance_account=binance_account,
                                          coinbase_account=coinbase_account)
            Logger.verbose_console_log(verbose=verbose,
                                       message=f"[CRYPTO] {coin_name} is currently valued at ${coin.price} per coin.",
                                       message_type=Message.MESSAGE_TYPE.STATUS)
            self.crypto_df = self.crypto_df.append(coin.to_series(update_time=update_time))
            self.crypto_df = self.crypto_df.sort_index()
            
        for stock_symbol, stock in self.stocks.items():
            stock.price = get_stock_price(symbol=stock_symbol)
            Logger.verbose_console_log(verbose=verbose,
                                       message=f"[STOCK] {stock.name} is currently valued at ${stock.price} per share.",
                                       message_type=Message.MESSAGE_TYPE.STATUS)
            self.stocks_df = self.stocks_df.append(stock.to_series(update_time=update_time))
            self.stocks_df = self.stocks_df.sort_index()

        for account_name, checking_account in self.checking_accounts.items():
            #checking_account.update()
            Logger.verbose_console_log(verbose=verbose,
                                       message="[CHECKING] " + account_name + " is currently valued at $" + str(checking_account.equity),
                                       message_type=Message.MESSAGE_TYPE.STATUS)
            self.checking_account_df = self.checking_account_df.append(checking_account.to_series(update_time=update_time))
            self.checking_account_df = self.checking_account_df.sort_index()

        for location, usd_in_float in self.floating_usd.items():
            self.floating_usd_df = self.floating_usd_df.append(Series({"datetime": update_time, "location": location, "equity": usd_in_float}, name=time()))
            self.floating_usd_df = self.floating_usd_df.sort_index()

        self.lock.release()

        Logger.verbose_console_log(verbose=verbose,
                                   message=str(type(self)) + " is finished updating.",
                                   message_type=Message.MESSAGE_TYPE.SUCCESS)

        if not self.initial_update.is_set():
            self.initial_update.set()

    def calculate_equity(self, holding_type: Union[str, Holdings.HOLDING_TYPE] = "all", verbose: bool = False) -> float:
        """[summary]

        Args:
            holding_type (Union[str, Holdings.HOLDING_TYPE], optional): [description]. Defaults to "all".

        Returns:
            float: [description]"""
        assert type(holding_type) == str or type(holding_type) == Holdings.HOLDING_TYPE

        Logger.verbose_console_log(verbose=verbose,
                                   message=str(type(self)) + " is calculating the equity of holding_type: " + str(holding_type),
                                   message_type=Message.MESSAGE_TYPE.STATUS)

        equity: float = 0.

        if type(holding_type) == str:
            holding_type: Holdings.HOLDING_TYPE = Holdings.HOLDING_TYPE(holding_type)

        if holding_type == Holdings.HOLDING_TYPE.STOCK or holding_type == Holdings.HOLDING_TYPE.ALL:
            equity += Holdings.calculate_holding_equity(holdings=self.stocks, verbose=verbose)
        if holding_type == Holdings.HOLDING_TYPE.CRYPTOCURRENCY or holding_type == Holdings.HOLDING_TYPE.ALL:
            equity += Holdings.calculate_holding_equity(holdings=self.cryptocoins, verbose=verbose)
        if holding_type == Holdings.HOLDING_TYPE.CHECKING or holding_type == Holdings.HOLDING_TYPE.ALL:
            equity += Holdings.calculate_holding_equity(holdings=self.checking_accounts, verbose=verbose)
        if (holding_type == Holdings.HOLDING_TYPE.FLOATING_USD or holding_type == Holdings.HOLDING_TYPE.ALL) and self.floating_usd is not None:
            equity += Holdings.calculate_holding_equity(holdings=self.floating_usd, verbose=verbose)

        Logger.verbose_console_log(verbose=verbose,
                                   message=str(type(self)) + " equity of holding_type: " + str(holding_type) + " = " + "$%.2f" % equity,
                                   message_type=Message.MESSAGE_TYPE.SUCCESS)

        return equity

    def sum_equities(self, holding_type: Holdings.HOLDING_TYPE, time: float) -> float:
        total_equity = 0.

        if holding_type == Holdings.HOLDING_TYPE.CRYPTOCURRENCY or holding_type == Holdings.HOLDING_TYPE.ALL:
            crypto_at_time: DataFrame = self.crypto_df[self.crypto_df.datetime == time]
            crypto_equity = crypto_at_time.quantity * crypto_at_time.price
            total_equity += crypto_equity.sum()

        if holding_type == Holdings.HOLDING_TYPE.STOCK or holding_type == Holdings.HOLDING_TYPE.ALL:
            stocks_at_time: DataFrame = self.stocks_df[self.stocks_df.datetime == time]
            stock_equity = stocks_at_time.quantity * stocks_at_time.price
            total_equity += stock_equity.sum()

        if holding_type == Holdings.HOLDING_TYPE.CHECKING or holding_type == Holdings.HOLDING_TYPE.ALL:
            total_equity += self.checking_account_df[self.checking_account_df.datetime == time]['equity'].sum()

        if holding_type == Holdings.HOLDING_TYPE.FLOATING_USD or holding_type == Holdings.HOLDING_TYPE.ALL:
            total_equity += self.floating_usd_df[self.floating_usd_df.datetime == time]['equity'].sum()
        
        return total_equity

    def calculate_holding_equities(self, holding_type: Holdings.HOLDING_TYPE, times: array) -> array:
        """[summary]

        Args:
            holding_type (Holdings.HOLDING_TYPE): [description]
            times (array): [description]

        Returns:
            array: [description]"""
        return array([self.sum_equities(holding_type=holding_type, time=time) for time in times])

    def get_times(self, holding_type: Holdings.HOLDING_TYPE) -> array:
        """[summary]

        Args:
            holding_type (Holdings.HOLDING_TYPE): [description]

        Returns:
            [type]: [description]"""
        if holding_type == Holdings.HOLDING_TYPE.ALL:
            stock_times = self.stocks_df['datetime'].unique().tolist()
            crypto_times = self.crypto_df['datetime'].unique().tolist()
            checking_times = self.checking_account_df['datetime'].unique().tolist()
            floating_times = self.floating_usd_df['datetime'].unique().tolist()
            return array(sorted(list(set(stock_times + crypto_times + checking_times + floating_times))))
        elif holding_type == Holdings.HOLDING_TYPE.STOCK:
            return array(self.stocks_df['datetime'].unique())
        elif holding_type == Holdings.HOLDING_TYPE.CRYPTOCURRENCY:
            return array(self.crypto_df['datetime'].unique())
        elif holding_type == Holdings.HOLDING_TYPE.CHECKING:
            return array(self.checking_account_df['datetime'].unique())
        elif holding_type == Holdings.HOLDING_TYPE.FLOATING_USD:
            return array(self.floating_usd_df['datetime'].unique())

    @staticmethod
    def calculate_holding_equity(holdings: Union[Dict[str, Holdings.Stock],
                                                 Dict[str, Holdings.Cryptocoin], 
                                                 Dict[str, Holdings.CheckingAccount],
                                                 Dict[str, float]],
                                 verbose: bool = False) -> float:
        """[summary]

        Args:
            holdings (Union[Dict[str, Holdings.Stock], 
                            Dict[str, Holdings.Cryptocoin], 
                            Dict[str, Holdings.CheckingAccount], 
                            Dict[str, Holdings.FloatingUSD]]): [description]
            verbose (bool, optional): [description]. Defaults to False.

        Returns:
            float: [description]"""
        total_equity: float = 0.
        if len(holdings.keys()) > 0:
            equity_type: Callable = type(holdings[list(holdings.keys())[0]])
        else:
            return 0.

        for holding_name, holding in holdings.items():
            if equity_type == float or equity_type == int:
                holding_equity = holding
            else:
                holding_equity = holding.calculate_equity()
            total_equity += holding_equity

            Logger.verbose_console_log(verbose=verbose,
                                       message=str(holding_name) + " has a " + str(equity_type) + " value of " + "$%.2f" % holding_equity,
                                       message_type=Message.MESSAGE_TYPE.STATUS)

        Logger.verbose_console_log(verbose=verbose,
                                   message=str(Holdings) + " has calculated a total " + str(equity_type) + " equity of " + "$%.2f" % total_equity,
                                   message_type=Message.MESSAGE_TYPE.SUCCESS)

        return total_equity

    @staticmethod
    def load(holding_file_name: str, file_name_cipher: VigenereCipher, data_cipher: VigenereCipher, mint: Union[Mint, None]) -> Holdings:
        """[summary]

        Args:
            holding_file_name (str): [description]

        Returns:
            Holdings: [description]"""
        stocks: Dict[str, Holdings.Stock] = {}
        crypto: Dict[str, Holdings.Cryptocoin] = {}
        checking_accounts: Dict[str, Holdings.CheckingAccount] = {}
        floating_usd: Dict[str, float] = {}

        stock_and_crypto_holdings: Dict[str, Dict[str, Dict[str, Any]]] = load_json_resource(file_name_cipher=file_name_cipher, 
                                                                                             data_cipher=data_cipher, 
                                                                                             resource_file_name=holding_file_name)

        # Load stocks
        for stock_symbol, stock_data in stock_and_crypto_holdings['stock'].items():
            stocks[stock_symbol] = Holdings.Stock(symbol=stock_symbol,
                                                  name=stock_data['name'],
                                                  quantity=stock_data['quantity'],
                                                  cost_basis_per_share=stock_data['cost basis per share'])
        # Load crypto
        for coin, coin_data in stock_and_crypto_holdings['crypto'].items():
            crypto[coin] = Holdings.Cryptocoin(name=coin_data["name"],
                                               coin=coin,
                                               quantity=coin_data['quantity'],
                                               investment=coin_data['investment'])

        # Load float
        for float_location, usd_in_float in stock_and_crypto_holdings['float'].items():
            floating_usd[float_location] = usd_in_float

        # Load checking accounts from mint
        if mint is not None:
            for account_data in mint.get_accounts(False):
                checking_accounts[account_data['accountName']] = Holdings.CheckingAccount(name=account_data['accountName'],
                                                                                        equity=account_data['value'])
            mint.close()

        return Holdings(stocks=stocks,
                        cryptocoins=crypto, 
                        checking_accounts=checking_accounts,
                        floating_usd=floating_usd)

    class Holding(ABC, object):
        """[summary]"""
        @abstractclassmethod
        def __str__(self) -> str:
            """[summary]

            Returns:
                str: [description]"""
            pass

        @abstractclassmethod
        def calculate_equity(self) -> float:
            """TODO"""
            pass

        @abstractstaticmethod
        def to_series(self, update_time: float) -> Series:
            """[summary]

            Args:
                update_time (float): [description]

            Returns:
                Series: [description]"""
            pass

        @abstractclassmethod
        def get_columns() -> List[str]:
            """[summary]

            Returns:
                List[str]: [description]"""
            pass

    class Cryptocoin(Holding):
        """[summary]"""
        def __init__(self, name: str, coin: str, quantity: float, investment: float,
                     unrealized_rewards: float = 0.0):
            """Constructor.

            Args:
                name (str): [description]
                quantity (float): [description]
                investment (float): [description]
                gain (float): [description]
                unrealized_rewards (float, optional): [description]. Defaults to 0.0."""
            self.name: str = name
            self.coin: str = coin
            self.quantity: float = quantity
            self.unrealized_rewards: float = unrealized_rewards
            self.investment: float = investment
            self.price = None

        def __str__(self) -> str:
            """[summary]

            Returns:
                str: [description]"""
            return str({"name": self.name, "quantity": self.quantity, 
                        "unrealized_rewards": self.unrealized_rewards, "cost basis per coin": self.investment / self.quantity, 
                        "price": self.price})

        def calculate_equity(self) -> float:
            """[summary]

            Returns:
                float: [description]"""
            assert self.price is not None, "Equity cannot be calculated without initially updating price."
            return self.quantity * self.price

        def generate_database_table(self, database_script: TextIO):
            """[summary]

            Args:
                database_script (TextIO): [description]"""
            database_script.write("CREATE TABLE {}(\n".format(self.coin))
            database_script.write("    datetime DATETIME PRIMARY KEY,\n")
            database_script.write("    quantity float,\n")
            database_script.write("    stake float,\n")
            database_script.write("    unrealized_rewards float,\n")
            database_script.write("    investment float,\n")
            database_script.write("    price float);\n\n")

        def to_series(self, update_time: float) -> Series:
            """[summary]

            Args:
                update_time (datetime): [description]

            Returns:
                Series: [description]"""
            return Series({"datetime": update_time, "name": self.name, "investment": self.investment,
                           "quantity": self.quantity, "price": self.price},
                          name=time())

        @staticmethod
        def get_columns() -> List[str]:
            """[summary]

            Returns:
                List[str]: [description]"""
            return ["datetime", "name", "investment", "quantity", "price"]

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

        def __str__(self) -> str:
            """[summary]

            Returns:
                str: [description]"""
            return str({"symbol": self.symbol, "name": self.name, "cost_basis_per_share": self.cost_basis_per_share, 
                        "quantity": self.quantity, "price": self.price})

        def calculate_equity(self) -> float:
            """[summary]

            Returns:
                float: [description]"""
            assert self.price is not None, "Equity cannot be calculated without initially updating price."
            return self.quantity * self.price

        def generate_database_table(self, database_script: TextIO):
            """[summary]

            Args:
                database_script (TextIO): [description]"""
            database_script.write("CREATE TABLE {}(\n".format(self.symbol))
            database_script.write("    datetime DATETIME PRIMARY KEY,\n")
            database_script.write("    quantity float,\n")
            database_script.write("    cost_basis_per_share float,\n")
            database_script.write("    price float);\n\n")

        def to_series(self, update_time: float) -> Series:
            """[summary]

            Args:
                update_time (datetime): [description]

            Returns:
                Series: [description]"""
            return Series({"datetime": update_time, "stock": self.symbol, "cost_basis_per_share": self.cost_basis_per_share,
                           "quantity": self.quantity, "price": self.price},
                          name=time())

        @staticmethod
        def get_columns() -> List[str]:
            """[summary]

            Returns:
                List[str]: [description]"""
            return ["datetime", "stock", "cost_basis_per_share", "quantity", "price"]

    class CheckingAccount(Holding):
        """[summary]"""
        def __init__(self, name: str, equity: float):
            """Constructor.

            Args:
                name (str): [description]
                balance (float): [description]"""
            self.name = name
            self.equity = equity

        def __str__(self) -> str:
            """[summary]

            Returns:
                str: [description]"""
            return str({"name": self.name, "equity": self.equity})

        def calculate_equity(self) -> float:
            """[summary]

            Returns:
                float: [description]"""
            return self.equity

        @staticmethod
        def get_columns() -> List[str]:
            """[summary]

            Returns:
                List[str]: [description]"""
            return ["datetime", "account_name", "equity"]

        def to_series(self, update_time: float) -> Series:
            """[summary]

            Args:
                update_time (datetime): [description]

            Returns:
                Series: [description]"""
            return Series({"datetime": update_time, "account_name": self.name, "equity": self.equity},
                          name=time())

        def update(self, stocker: object) -> None:
            """[summary]

            Args:
                stocker (object): [description]"""
            mint_accounts_data = stocker.mint.get_accounts()

            matching_account_data = [account_data for account_data in mint_accounts_data if account_data['accountName'] == self.name]

            assert len(matching_account_data) == 1, "An unexpected number of matching account data was found: " + str(len(matching_account_data))

            self.equity = matching_account_data[0]['amount']

    @unique
    class HOLDING_TYPE(Enum):
        """[summary]"""
        ALL = "all"
        STOCK = "stock"
        CRYPTOCURRENCY = "crypto"
        CHECKING = "checking account"
        FLOATING_USD = "float"
