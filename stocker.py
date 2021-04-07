#/usr/bin/env python
"""stocker.py:"""

__author__ = "Jacob T. Cassady"
__email__ = "jacobtaylorcassady@outlook.com"

# Built-in Modules
from utilities.Logger import Logger
from argparse import ArgumentParser
from sys import argv, exit
from typing import Callable, Dict, Any
from os.path import join, dirname
from json import loads

# 3rd party Modules
from PyQt5.QtWidgets import QApplication, QMainWindow
from qdarkstyle import load_stylesheet

# Stocker Library Modules
from utilities.Cipher import initialize_lock_and_key_ciphers
from utilities.Logger import Logger
from interfaces.binance_us import BinanceInterface
from interfaces.mint import Mint
from windows.control import ControlWindow
from windows.pie import PieDisplay
from holdings import Holdings

RESOURCE_DIRECTORY = join(dirname(__file__), "resources")

class Stocker(object):
    """[summary]"""
    KEY_FILE_NAME: str = "keys.json"
    HOLDINGS_FILE_NAME: str = "holdings.json"
    PASS_FILE_NAME: str = "pass.json"
    USER_NAME: str = "jakeadelic"

    def __init__(self, verbose: bool = False):
        """Constructor.

        Args:
            verbose (bool, optional): [description]. Defaults to False."""
        if arguments.verbose:
            Logger.console_log(message="Stocker is initializing in verbose mode", message_type=Logger.MESSAGE_TYPE.STATUS)

        self.verbose = verbose
        self.ciphers: dict = initialize_lock_and_key_ciphers()
        self.keys: dict = self.load_resource(resource_file_name=Stocker.KEY_FILE_NAME)
        self.passes: dict = self.load_resource(resource_file_name=Stocker.PASS_FILE_NAME)[Stocker.USER_NAME]
        self.binance_interface = BinanceInterface(api_key=self.keys['binance.us']['API Key'], 
                                                  api_secret=self.keys['binance.us']['Secret Key'])
        self.mint = Mint(email=self.passes['mint']['email'],
                         password=self.passes['mint']['password'])
        self.holdings: Holdings = self.load_holdings(holding_file_name=Stocker.HOLDINGS_FILE_NAME)
        # Perform initial holdings price and balance update.
        self.holdings.update()

        # Reporting initial equities
        if verbose:
            self.holdings.calculate_equity(holding_type=Holdings.HOLDING_TYPE.ALL)

        self.generated_windows = {}

        # Open initial window.
        #self.open_window(window_class=PieDisplay)

        exit()

    def open_window(self, window_class: Callable[[], QMainWindow]) -> None:
        """Opens a window class and displays it.

        Args:
            window_class (Callable[[], QMainWindow]): [description]"""
        Logger.verbose_console_log(verbose=self.verbose,
                                   message=str(type(self)) + " is opening window: " + str(window_class),
                                   message_type=Logger.MESSAGE_TYPE.STATUS)

        window = window_class(stocker=self)

        if window_class in self.generated_windows.keys():
            self.generated_windows[window_class].append(window)
        else:
            self.generated_windows[window_class] = [window]

        window.show()

    def load_resource(self, resource_file_name: str) -> Dict[str, Any]:
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

    def load_holdings(self, holding_file_name: str) -> Holdings:
        """[summary]

        Args:
            holding_file_name (str): [description]

        Returns:
            Holdings: [description]"""
        stocks: Dict[str, Holdings.Stock] = {}
        crypto: Dict[str, Holdings.Cryptocoin] = {}
        checking_accounts: Dict[str, Holdings.CheckingAccount] = {}
        floating_usd: Dict[str, Holdings.FloatingUSD] = {}

        stock_and_crypto_holdings: Dict[str, Dict[str, Dict[str, Any]]] = self.load_resource(resource_file_name=holding_file_name)

        # Load stocks
        for stock_symbol, stock_data in stock_and_crypto_holdings['stock'].items():
            stocks[stock_symbol] = Holdings.Stock(symbol=stock_symbol,
                                                  name=stock_data['name'],
                                                  quantity=stock_data['quantity'],
                                                  cost_basis_per_share=stock_data['cost basis per share'])
        # Load crypto
        for crypto_symbol, crypto_data in stock_and_crypto_holdings['crypto'].items():
            crypto[crypto_symbol] = Holdings.Cryptocoin(symbol=crypto_symbol,
                                                        name=crypto_data["name"],
                                                        coin=crypto_data['coin'],
                                                        quantity=crypto_data['quantity'])

        # Load checking accounts from mint
        for account_data in self.mint.get_accounts(False):
            checking_accounts[account_data['accountName']] = Holdings.CheckingAccount(name=account_data['accountName'],
                                                                                      equity=account_data['value'])

        return Holdings(stocker=self, 
                        stocks=stocks,
                        cryptocoins=crypto, 
                        checking_accounts=checking_accounts,
                        floating_usd=floating_usd)



if __name__ == "__main__":
    # Determine if in debug mode
    parser = ArgumentParser()
    parser.add_argument("--verbose", "-v", help="verbose mode", default=True, required=False)
    arguments = parser.parse_args()

    app = QApplication(argv)
    stocker = Stocker(verbose=arguments.verbose)
    app.setStyleSheet(load_stylesheet(qt_api='pyqt5'))
    exit(app.exec_())
