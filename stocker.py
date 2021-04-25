#/usr/bin/env python
"""stocker.py:"""

__author__ = "Jacob T. Cassady"
__email__ = "jacobtaylorcassady@outlook.com"

# Built-in Modules
from threads.prices import PriceChecker
from argparse import ArgumentParser
from sys import argv, exit
from typing import Callable, Dict, Any
from os.path import join, dirname
from json import loads
from io import StringIO
from time import sleep

# 3rd party Modules
from PyQt5.QtWidgets import QApplication, QMainWindow
from qdarkstyle import load_stylesheet
from pandas import DataFrame, read_csv
from StatusLogger import Logger, Message

# Stocker Library Modules
from utilities.Cipher import initialize_lock_and_key_ciphers
from accounts.binance_us_account import BinanceAccount
from accounts.coinbase_account import CoinbaseAccount
from interfaces.mint import Mint
from windows.control import ControlWindow
from windows.EquityTracker import EquityTracker
from holdings import Holdings

RESOURCE_DIRECTORY = join(dirname(__file__), "resources")

class Stocker(object):
    """[summary]"""
    KEY_FILE_NAME: str = "keys.json"
    HOLDINGS_FILE_NAME: str = "holdings.json"
    PASS_FILE_NAME: str = "pass.json"
    COINBASE_TRANSACTION_HISTORY_FILE_NAME = "coinbase transaction history.csv"
    BINANCE_TRANSACTION_HISTORY_FILE_NAME = "binance transaction history.csv"
    DEPOSIT_HISTORY_FILE_NAME = "deposits.csv"
    USER_NAME: str = "jakeadelic"

    def __init__(self, verbose: bool = False):
        """Constructor.

        Args:
            verbose (bool, optional): [description]. Defaults to False."""
        Logger.verbose_console_log(verbose=arguments.verbose,
                                   message="Stocker is initializing in verbose mode", 
                                   message_type=Message.MESSAGE_TYPE.STATUS)

        self.verbose = verbose
        self.ciphers: dict = initialize_lock_and_key_ciphers()
        self.keys: dict = self.load_json_resource(resource_file_name=Stocker.KEY_FILE_NAME)
        self.passes: dict = self.load_json_resource(resource_file_name=Stocker.PASS_FILE_NAME)[Stocker.USER_NAME]
        deposit_history: DataFrame = self.load_csv_resource(resource_file_name=Stocker.DEPOSIT_HISTORY_FILE_NAME)
        self.binance_account = BinanceAccount(deposit_history=deposit_history[deposit_history.Service == "binance"],
                                              transaction_history=self.load_csv_resource(resource_file_name=Stocker.BINANCE_TRANSACTION_HISTORY_FILE_NAME),
                                              api_key=self.keys['binance.us']['API Key'], 
                                              api_secret=self.keys['binance.us']['Secret Key'])
        self.coinbase_account = CoinbaseAccount(deposit_history=deposit_history[deposit_history.Service == "coinbase"],
                                                transaction_history=self.load_csv_resource(resource_file_name=Stocker.COINBASE_TRANSACTION_HISTORY_FILE_NAME),
                                                api_key=self.keys['coinbase']['API Key'],
                                                api_secret=self.keys['coinbase']['API Secret'])
        self.mint = Mint(email=self.passes['mint']['email'],
                         password=self.passes['mint']['password'])
        self.holdings: Holdings = self.load_holdings(holding_file_name=Stocker.HOLDINGS_FILE_NAME)

        # Start price update thread
        price_checker_thread: PriceChecker = PriceChecker(stocker=self, verbose=self.verbose)
        price_checker_thread.start()
        self.holdings.initial_update.wait(timeout_ms=60000)

        self.generated_windows = {}

        # Open initial window.
        self.open_window(window_class=EquityTracker)

    def open_window(self, window_class: Callable[[], QMainWindow]) -> None:
        """Opens a window class and displays it.

        Args:
            window_class (Callable[[], QMainWindow]): [description]"""
        Logger.verbose_console_log(verbose=self.verbose,
                                   message=str(type(self)) + " is opening window: " + str(window_class),
                                   message_type=Message.MESSAGE_TYPE.STATUS)

        window = window_class(stocker=self)

        if window_class in self.generated_windows.keys():
            self.generated_windows[window_class].append(window)
        else:
            self.generated_windows[window_class] = [window]

        window.show()

    def load_json_resource(self, resource_file_name: str) -> Dict[str, Any]:
        """[summary]

        Args:
            resource_file_name (str): [description]

        Returns:
            Dict[str, Any]: [description]"""
        encoded_resource_file_name = self.ciphers['file_name'].encode(resource_file_name)

        with open(join(RESOURCE_DIRECTORY, encoded_resource_file_name), "r") as encoded_resource_file:
            encoded_resource_data = encoded_resource_file.read()

        decoded_resource_data = self.ciphers['data'].decode(encoded_resource_data)

        return loads(decoded_resource_data)

    def load_csv_resource(self, resource_file_name: str) -> DataFrame:
        """[summary]

        Args:
            resource_file_name (str): [description]

        Returns:
            DataFrame: [description]"""
        encoded_resource_file_name = self.ciphers['file_name'].encode(resource_file_name)

        with open(join(RESOURCE_DIRECTORY, encoded_resource_file_name), "r") as encoded_resource_file:
            encoded_resource_data = encoded_resource_file.read()

        decoded_resource_data = self.ciphers['data'].decode(encoded_resource_data)

        return read_csv(StringIO(decoded_resource_data), index_col=0)

    def load_holdings(self, holding_file_name: str) -> Holdings:
        """[summary]

        Args:
            holding_file_name (str): [description]

        Returns:
            Holdings: [description]"""
        stocks: Dict[str, Holdings.Stock] = {}
        crypto: Dict[str, Holdings.Cryptocoin] = {}
        checking_accounts: Dict[str, Holdings.CheckingAccount] = {}
        floating_usd: Dict[str, float] = {}

        stock_and_crypto_holdings: Dict[str, Dict[str, Dict[str, Any]]] = self.load_json_resource(resource_file_name=holding_file_name)

        # Load stocks
        for stock_symbol, stock_data in stock_and_crypto_holdings['stock'].items():
            stocks[stock_symbol] = Holdings.Stock(symbol=stock_symbol,
                                                  name=stock_data['name'],
                                                  quantity=stock_data['quantity'],
                                                  cost_basis_per_share=stock_data['cost basis per share'])
        # Load crypto
        for crypto_symbol, crypto_data in stock_and_crypto_holdings['crypto'].items():
            binance_investment_analysis = self.binance_account.analyze_investment(symbol=crypto_data['coin'])
            coinbase_investment_analysis = self.coinbase_account.analyze_investment(symbol=crypto_data['coin'])

            crypto[crypto_symbol] = Holdings.Cryptocoin(symbol=crypto_symbol,
                                                        name=crypto_data["name"],
                                                        coin=crypto_data['coin'],
                                                        quantity=crypto_data['quantity'],
                                                        investment=binance_investment_analysis['investment'] + coinbase_investment_analysis['investment'],
                                                        gain=binance_investment_analysis['return'] + coinbase_investment_analysis['return'])

        # Load float
        for float_location, usd_in_float in stock_and_crypto_holdings['float'].items():
            floating_usd[float_location] = usd_in_float

        # Load checking accounts from mint
        for account_data in self.mint.get_accounts(False):
            checking_accounts[account_data['accountName']] = Holdings.CheckingAccount(name=account_data['accountName'],
                                                                                      equity=account_data['value'])
        self.mint.close()

        return Holdings(stocker=self, 
                        stocks=stocks,
                        cryptocoins=crypto, 
                        checking_accounts=checking_accounts,
                        floating_usd=floating_usd)

    def get_crypto_price(self, coin_name: str) -> float:
        """[summary]

        Args:
            coin_name (str): [description]

        Returns:
            float: [description]"""
        try:
            return float(self.binance_account.interface.get_ticker(symbol=coin_name+"USD")['lastPrice'])
        except Exception as error:
            Logger.console_log(message="Exception {} found when attempting to get price from binance. Attempting again through coinbase.".format(error),
                                message_type=Message.MESSAGE_TYPE.MINOR_FAIL)
            try:
                return float(self.coinbase_account.interface.get_buy_price(currency_pair=coin_name+"-USD")['amount'])
            except Exception as error:
                Logger.console_log(message="Exception {} found when attempting to get price from coinbase. Calling get_crypto_price again.".format(error),
                                   message_type=Message.MESSAGE_TYPE.MINOR_FAIL)
                sleep(5 * 60)
                return self.get_crypto_price(coin_name=coin_name)



if __name__ == "__main__":
    # Determine if in debug mode
    parser = ArgumentParser()
    parser.add_argument("--verbose", "-v", help="verbose mode", default=True, required=False)
    arguments = parser.parse_args()

    app = QApplication(argv)
    stocker = Stocker(verbose=arguments.verbose)
    app.setStyleSheet(load_stylesheet(qt_api='pyqt5'))
    exit(app.exec_())
