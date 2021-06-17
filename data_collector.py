#/usr/bin/env python
"""data_collector.py:"""
from __future__ import annotations

__author__ = "Jacob T. Cassady"
__email__ = "jacobtaylorcassady@outlook.com"

from enum import Enum
from datetime import datetime
from time import sleep
from typing import Dict, Any, List
from threading import Thread
from multiprocessing import cpu_count

from StatusLogger import Logger, Message

from utilities.Cipher import initialize_lock_and_key_ciphers, load_json_resource, VigenereCipher
from interfaces.mint import Mint
from holdings import Holdings


class DataCollector(Thread):
    """Scraper Server object"""
    SERVER_NAME: str = "DataCollector"
    HOLDINGS_FILE_NAME: str = "holdings.json"
    PASS_FILE_NAME: str = "pass.json"
    USER_NAME: str = "jakeadelic"

    def __init__(self, verbose: bool = True, log: bool = False, 
                 overwrite_log: bool = False) -> None:
        Thread.__init__(self)
        self.available_cpus = cpu_count() - 1
        self.logger = Logger(name=DataCollector.SERVER_NAME, file_log=log, verbose=verbose, overwrite=overwrite_log)
        self.ciphers: Dict[str, VigenereCipher] = initialize_lock_and_key_ciphers()
        self.passes: dict = load_json_resource(file_name_cipher=self.ciphers["file_name"], 
                                               data_cipher=self.ciphers['data'], 
                                               resource_file_name=DataCollector.PASS_FILE_NAME)[DataCollector.USER_NAME]
        self.mint = Mint(email=self.passes['mint']['email'],
                         password=self.passes['mint']['password'])
        self.mode: DataCollector.SERVER_MODE = DataCollector.SERVER_MODE.INVALID

        self.threads = {}
        # Initialize Threads
        # Build worker threads for available number of cpus
        self.threads[DataCollector.WorkerThread] = []
        for available_cpu_index in range(self.available_cpus):
            self.threads[DataCollector.WorkerThread].append(
                DataCollector.WorkerThread(thread_id=available_cpu_index, scraper_server=self))

        # Build Executive Thread
        self.threads[DataCollector.ExecutiveThread] = DataCollector.ExecutiveThread(thread_id=0, scraper_server=self,
                                                                                    worker_threads=self.threads[DataCollector.WorkerThread])

    def run(self) -> None:
        """
        """
        self.logger.start()
        self.logger.log(message="Starting " + DataCollector.SERVER_NAME, 
                        message_type=Message.MESSAGE_TYPE.STATUS)

        self.threads[DataCollector.ExecutiveThread].start()

        # Start Worker Threads
        for worker_thread in self.threads[DataCollector.WorkerThread]:
            worker_thread.start()

        # Wait for Worker Threads to Complete
        for worker_thread in self.threads[DataCollector.WorkerThread]:
            worker_thread.join()

        # Wait for Executive Thread to Complete
        self.threads[DataCollector.ExecutiveThread].join()

        """
        try:
            while mode != DataCollector.SERVER_MODE.SHUTTING_DOWN:
                mode: DataCollector.SERVER_MODE = DataCollector.SERVER_MODE.set_mode()                

                if mode == DataCollector.SERVER_MODE.STOCK_MARKET_OPEN:
                    pass
                elif mode == DataCollector.SERVER_MODE.STOCK_MARKET_CLOSED:
                    pass

                self.logger.log(message=f"{DataCollector.SERVER_NAME} is running in mode {mode}.", 
                                message_type=Message.MESSAGE_TYPE.STATUS)

                sleep(1)
        except (KeyboardInterrupt, SystemExit) as error:
            self.logger.log(message=f"{DataCollector.SERVER_NAME} is shutting down due to exception: {error}", 
                            message_type=Message.MESSAGE_TYPE.STATUS)
        """

        self.logger.stop()

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
        for coin, coin_data in stock_and_crypto_holdings['crypto'].items():
            crypto[coin] = Holdings.Cryptocoin(name=coin_data["name"],
                                               coin=coin,
                                               quantity=coin_data['quantity'],
                                               investment=coin_data['investment'])

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

    class ExecutiveThread(Thread):
        """[summary]"""

        def __init__(self, thread_id: int, data_collector: DataCollector, worker_threads: list):
            """[summary]

            Args:
                thread_id (int): [description]
                scraper_server (object): [description]
                worker_threads (list): [description]"""
            Thread.__init__(self)
            self.thread_id = thread_id
            self.data_collector = data_collector
            self.worker_threads = worker_threads

        def __str__(self) -> str:
            """
            """
            return str(type(self)) + "_" + str(self.thread_id)

        def run(self) -> None:
            """TODO"""
            pass

    class WorkerThread(Thread):
        """[summary]"""

        def __init__(self, thread_id: int, data_collector: DataCollector):
            """
            Constructor.
            :param thread_id:
            :param scraper_server:
            """
            Thread.__init__(self)
            self.thread_id = thread_id
            self.data_collector: DataCollector = data_collector
            self.holdings_to_update: List[Holdings.Holding] = []

        def __str__(self) -> str:
            """
            """
            return str(type(self)) + "_" + str(self.thread_id)

        def run(self) -> None:
            """TODO"""
            pass

    class SERVER_MODE(Enum):
        INVALID = "invalid"
        STOCK_MARKET_OPEN = "stock market open"
        STOCK_MARKET_CLOSED = "stock market closed"
        SHUTTING_DOWN = "shutting down"

        @staticmethod
        def set_mode() -> DataCollector.SERVER_MODE:
            """[summary]

            Returns:
                DataCollector.SERVER_MODE: [description]"""
            right_now = datetime.now()
            right_now_hour = int(right_now.hour)
            right_now_minute = int(right_now.minute)

            minutes = right_now_hour * 60 + right_now_minute

            # If we are between 9:30 am and 4 pm the stock market is open
            if 960 > minutes > 570 and is_datetime_weekday(current_time=datetime.now()):
                return DataCollector.SERVER_MODE.STOCK_MARKET_OPEN
            else:
                return DataCollector.SERVER_MODE.STOCK_MARKET_CLOSED

def is_datetime_weekday(current_time: datetime):
    return current_time.isoweekday() in range(1, 6)


if __name__ == "__main__":
    test_data_collection_server = DataCollector()
    test_data_collection_server.run()