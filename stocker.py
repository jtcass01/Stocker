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
from os import getcwd
from json import loads
from io import StringIO

# 3rd party Modules
from PyQt5.QtWidgets import QApplication, QMainWindow
from qdarkstyle import load_stylesheet
from pandas import DataFrame, read_csv
from StatusLogger import Logger, Message

# Stocker Library Modules
from utilities.Cipher import initialize_lock_and_key_ciphers, load_json_resource
from accounts.binance_us_account import BinanceAccount
from accounts.coinbase_account import CoinbaseAccount
from interfaces.mint import Mint
from database_management.generate_my_sql_script import generate_stocker_database_scripts
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
        self.keys: dict = load_json_resource(file_name_cipher=self.ciphers["file_name"], 
                                             data_cipher=self.ciphers['data'], 
                                             resource_file_name=Stocker.KEY_FILE_NAME)
        self.passes: dict = load_json_resource(file_name_cipher=self.ciphers["file_name"], 
                                               data_cipher=self.ciphers['data'], 
                                               resource_file_name=Stocker.PASS_FILE_NAME)[Stocker.USER_NAME]
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
        self.holdings: Holdings = Holdings.load(holding_file_name=Stocker.HOLDINGS_FILE_NAME, 
                                                file_name_cipher=self.ciphers['file_name'], 
                                                data_cipher=self.ciphers['data'], 
                                                mint=self.mint)

        # Start price update thread
        self.price_checker_thread: PriceChecker = PriceChecker(stocker=self, verbose=self.verbose)
        self.price_checker_thread.start()
        self.holdings.initial_update.wait(timeout_ms=60000)

        self.generated_windows = {}

    def stop(self) -> None:
        self.price_checker_thread.stop()

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

if __name__ == "__main__":
    # Determine if in debug mode
    parser = ArgumentParser()
    parser.add_argument("--verbose", "-v", help="verbose mode", default=True, required=False)
    parser.add_argument("--generate_database", "-gdb", help="generate sql scripts for databsae", default=False, required=False)
    arguments = parser.parse_args()

    if arguments.generate_database:
        stocker = Stocker(verbose=arguments.verbose)

        generate_stocker_database_scripts(holdings=stocker.holdings,
                                          database_sql_script_location = join(getcwd(), "MarketDB.sql"),
                                          database_name = "Stocker_Market_Data")

        stocker.stop()

        exit()
    else:
        app = QApplication(argv)
        stocker = Stocker(verbose=arguments.verbose)
        app.setStyleSheet(load_stylesheet(qt_api='pyqt5'))
        stocker.open_window(window_class=EquityTracker)
        exit(app.exec_())
