import json
import os
from bs4 import BeautifulSoup
from urllib.request import urlopen
from datetime import datetime
from pandas import DataFrame, read_pickle
from numpy import array
from typing import Union
from string import ascii_uppercase
from enum import IntEnum
from time import sleep
from threading import Thread, Lock
from multiprocessing import cpu_count
from itertools import product
import numpy as np

from utilities.Logger import Logger


class Scraper(object):
    """
    Scraper Server object
    """

    def __init__(self, data_refresh_rate: int = 1800, relative_path_correction: str = "") -> None:
        """
        Constructor.
        :param data_refresh_rate:
        :param relative_path_correction:
        """
        Logger.console_log("Initializing Stock Scraper.", status=Logger.LogStatus.COMMUNICATION)
        self.scrape = True
        self.available_cpus = cpu_count() - 1
        self.threads = {}
        self.mode_lock = Lock()
        self.executive_lock = Lock()
        self.mode = Scraper.ServerModes.INVALID
        self.stock_ticker_letters_to_survey = list(ascii_uppercase)
        self.relative_path_correction = relative_path_correction

        # Initialize Threads
        # Build worker threads for available number of cpus
        self.threads[Scraper.WorkerThread] = []
        for available_cpu_index in range(self.available_cpus):
            self.threads[Scraper.WorkerThread].append(
                Scraper.WorkerThread(thread_id=available_cpu_index, scraper_server=self))
        # Build Executive Thread
        self.threads[Scraper.ExecutiveThread] = Scraper.ExecutiveThread(thread_id=0, scraper_server=self,
                                                                        worker_threads=self.threads[
                                                                            Scraper.WorkerThread])

    def __del__(self) -> None:
        """
        Deconstructor.
        """
        self.mode = Scraper.ServerModes.SHUT_DOWN

    def run(self) -> None:
        """
        """
        # Start Executive Thread
        self.threads[Scraper.ExecutiveThread].start()

        # Start Worker Threads
        for worker_thread in self.threads[Scraper.WorkerThread]:
            worker_thread.start()

        # Wait for Worker Threads to Complete
        for worker_thread in self.threads[Scraper.WorkerThread]:
            worker_thread.join()

        # Wait for Executive Thread to Complete
        self.threads[Scraper.ExecutiveThread].join()

    class ServerModes(IntEnum):
        INVALID = 0
        RETRIEVE_DATA = 1
        SURVEY_MARKET = 2
        SHUT_DOWN = 3

        @staticmethod
        def set_mode() -> IntEnum:
            """
            :return:
            """
            right_now = datetime.now()
            right_now_hour = int(right_now.hour)
            right_now_minute = int(right_now.minute)

            minutes = right_now_hour * 60 + right_now_minute

            # If we are between 9:30 am and 4 pm the stock market is open
            if 960 > minutes > 570 and is_datetime_weekday(current_time=datetime.now()):
                return Scraper.ServerModes.RETRIEVE_DATA
            else:
                return Scraper.ServerModes.SURVEY_MARKET

    class ExecutiveThread(Thread):
        """
        """

        def __init__(self, thread_id: int, scraper_server: object, worker_threads: list):
            """
            Constructor.
            :param thread_id:
            :param scraper_server:
            :param worker_threads:
            """
            super(Scraper.ExecutiveThread, self).__init__()
            self.thread_id = thread_id
            self.scraper_server = scraper_server
            self.worker_threads = worker_threads

        def __str__(self) -> str:
            """
            """
            return str(type(self)) + "_" + str(self.thread_id)

        def run(self) -> None:
            """
            """
            try:
                last_polled_server_mode = Scraper.ServerModes.INVALID

                while last_polled_server_mode != Scraper.ServerModes.SHUT_DOWN:

                    # Set the mode of the scraper server
                    self.scraper_server.mode_lock.acquire()
                    self.scraper_server.mode = Scraper.ServerModes.set_mode()

                    # The mode has changed.  It is time to update data for the workers.
                    if last_polled_server_mode != self.scraper_server.mode:
                        Logger.console_log(str(self) + " has updated the scraper server mode to " +
                                           str(self.scraper_server.mode) + " the time is " +
                                           str(datetime.now()), status=Logger.LogStatus.COMMUNICATION)
                        # The server mode is updated. Time to update the data
                        if self.scraper_server.mode == Scraper.ServerModes.SURVEY_MARKET:
                            # Give workers a list of stocks to monitor Get letters to be surveyed by workers
                            worker_starter_letters = self.scraper_server.stock_ticker_letters_to_survey[
                                                     :self.scraper_server.available_cpus]

                            # Remove worker starter letters from survey list
                            for worker_starter_letter in worker_starter_letters:
                                self.scraper_server.stock_ticker_letters_to_survey.remove(worker_starter_letter)

                            for worker_enum, worker_starter_letter in enumerate(worker_starter_letters):
                                Logger.console_log(str(self) + " is asking " + str(self.worker_threads[worker_enum]) +
                                                   " to survey letter " + worker_starter_letter,
                                                   Logger.LogStatus.COMMUNICATION)

                                # Get last surveyed ticker
                                previous_ticker_list = Scraper.FileHandler.load_tickers(
                                    ticker_starting_letter=worker_starter_letter,
                                    relative_path_correction=self.scraper_server.relative_path_correction)
                                if len(previous_ticker_list) > 0:
                                    last_surveyed_ticker = previous_ticker_list[-1]
                                else:
                                    last_surveyed_ticker = None

                                # Get new survey list.
                                ticker_survey_list = Scraper.get_ticker_survey_list(
                                    starting_letter=worker_starter_letter,
                                    last_ticker_surveyed=last_surveyed_ticker)

                                # Give the list to the worker
                                self.scraper_server.executive_lock.acquire()
                                self.worker_threads[worker_enum].ticker_survey_list = ticker_survey_list
                                self.scraper_server.executive_lock.release()

                        elif self.scraper_server.mode == Scraper.ServerModes.RETRIEVE_DATA:
                            # Get ticker data
                            ticker_list = Scraper.FileHandler.load_all_tickers(
                                relative_path_correction=self.scraper_server.relative_path_correction)
                            ticker_sub_lists = np.array_split(ticker_list, self.scraper_server.available_cpus)

                            # Give the ticker sub lists to workers to monitor for the day.
                            self.scraper_server.executive_lock.acquire()
                            for worker_enum, worker in enumerate(self.worker_threads):
                                Logger.console_log(str(self) + " is asking " + str(worker) +
                                                   " to monitor tickers: " + str(ticker_sub_lists[worker_enum]),
                                                   Logger.LogStatus.COMMUNICATION)
                                worker.ticker_monitor_list = ticker_sub_lists[worker_enum]
                            self.scraper_server.executive_lock.release()

                        # Update the mode
                        last_polled_server_mode = self.scraper_server.mode
                        self.scraper_server.mode_lock.release()
                    else:
                        self.scraper_server.mode_lock.release()

                        # Mode has not changed. Make sure the workers have work to do.
                        if last_polled_server_mode == Scraper.ServerModes.SURVEY_MARKET:
                            # Check to see if any of the workers have exhausted their lists
                            for worker in self.worker_threads:
                                if len(worker.ticker_survey_list) == 0:
                                    # wait 2 seconds to make sure the worker is finished
                                    sleep(2)

                                    # Get a new letter
                                    new_letter = self.scraper_server.stock_ticker_letters_to_survey.pop(0)

                                    # Get a new ticker survey list for the worker thread
                                    self.scraper_server.executive_lock.acquire()
                                    Logger.console_log(message=str(worker) + " has finished their survey. " + str(
                                        self) + " is asking it to survey " + new_letter + " next.",
                                                       status=Logger.LogStatus.COMMUNICATION)
                                    worker.ticker_survey_list = Scraper.get_ticker_survey_list(
                                        starting_letter=new_letter,
                                        last_ticker_surveyed=Scraper.FileHandler.get_last_ticker_surveyed(
                                            ticker_starting_letter=new_letter,
                                            relative_path_correction=self.scraper_server.relative_path_correction))
                                    self.scraper_server.executive_lock.release()

            except (KeyboardInterrupt, SystemExit):
                Logger.console_log(message="Executive" + str(self.thread_id) + "shutting down server",
                                   status=Logger.LogStatus.FAIL)
                self.scraper_server.mode_lock.acquire()
                self.scraper_server.mode = Scraper.ServerModes.SHUT_DOWN
                self.scraper_server.mode_lock.release()

    class WorkerThread(Thread):
        """
        """

        def __init__(self, thread_id: int, scraper_server: object):
            """
            Constructor.
            :param thread_id:
            :param scraper_server:
            """
            super(Scraper.WorkerThread, self).__init__()
            self.thread_id = thread_id
            self.scraper_server = scraper_server
            self.ticker_monitor_letter = None  # Set by Executive Thread
            self.ticker_survey_list = []
            self.ticker_monitor_list = []

        def __str__(self) -> str:
            """
            """
            return str(type(self)) + "_" + str(self.thread_id)

        def run(self) -> None:
            """
            """
            try:
                last_polled_server_mode = Scraper.ServerModes.INVALID
                ticker_survey_list = self.ticker_survey_list
                ticker_monitor_list = self.ticker_monitor_list

                while last_polled_server_mode != Scraper.ServerModes.SHUT_DOWN:
                    if last_polled_server_mode == Scraper.ServerModes.SURVEY_MARKET:
                        # Survey the market, it must be closed.
                        if len(ticker_survey_list) == 0:
                            # No data yet... sleep
                            sleep(5)
                            if self.scraper_server.executive_lock.acquire(blocking=False):
                                ticker_survey_list = self.ticker_survey_list
                                self.scraper_server.executive_lock.release()
                        else:
                            # Get ticker to survey.
                            ticker = self.ticker_survey_list[0]

                            # Log Result.
                            if Scraper.survey_ticker(thread=self, ticker=ticker):
                                self.scraper_server.executive_lock.acquire()
                                Scraper.FileHandler.add_ticker_to_tickers(ticker=ticker,
                                                                          relative_path_correction=self.scraper_server.relative_path_correction)
                                self.scraper_server.executive_lock.release()

                            # remove from survey list.
                            self.ticker_survey_list.remove(ticker)
                    elif last_polled_server_mode == Scraper.ServerModes.RETRIEVE_DATA:
                        # Stock market is open schedule
                        if len(ticker_monitor_list) == 0:
                            # The ticker monitor list is currently empty. Create non blocking check for tickers to monitor.
                            if self.scraper_server.executive_lock.acquire(blocking=False):
                                ticker_monitor_list = self.ticker_monitor_list
                                self.scraper_server.executive_lock.release()
                        else:
                            # Survey the current ticker_monitor_list
                            for ticker in ticker_monitor_list:
                                try:
                                    ticker_data = Scraper.WebInterface.get_current_ticker_data(ticker=ticker)
                                    Scraper.FileHandler.store_ticker_data(ticker=ticker, data=ticker_data,
                                                                          relative_path_correction=self.scraper_server.relative_path_correction)
                                    Logger.console_log(message=str(self) + " was able to retrieve data for ticker: "
                                                               + ticker + ".", status=Logger.LogStatus.SUCCESS)
                                except Exception as e:
                                    Logger.console_log(message=str(self) + " was unable to retrieve data for ticker: "
                                                               + ticker + " due to exception [" + str(e) +
                                                               "] trying again in 3 seconds.",
                                                       status=Logger.LogStatus.FAIL)
                                    sleep(3)
                                    try:
                                        ticker_data = Scraper.WebInterface.get_current_ticker_data(ticker=ticker)
                                        Scraper.FileHandler.store_ticker_data(ticker=ticker,
                                                                              data=ticker_data,
                                                                              relative_path_correction=self.scraper_server.relative_path_correction)
                                        Logger.console_log(message=str(self) + " was able to retrieve data for ticker: "
                                                                   + ticker + ".", status=Logger.LogStatus.SUCCESS)
                                    except ValueError:
                                        Logger.console_log(
                                            message=str(self) + " was unable to retrieve data for ticker again: "
                                            + ticker + " due to ValueError. Will try again later.",
                                            status=Logger.LogStatus.FAIL)
                                    except TypeError:
                                        Logger.console_log(
                                            message=str(self) + " was unable to retrieve data for ticker again: "
                                            + ticker + " due to TypeError. It is likely not a valid ticker. Removing" +
                                            "from list of valid tickers.",
                                            status=Logger.LogStatus.FAIL)
                                        Scraper.FileHandler.remove_invalid_ticker(ticker=ticker,
                                                                                  relative_path_correction=self.scraper_server.relative_path_correction)
                                    except Exception as e:
                                        Logger.console_log(
                                            message=str(self) + " was unable to retrieve data for ticker again: "
                                            + ticker + " due to exception " + str(e) + ".",
                                            status=Logger.LogStatus.FAIL)

                    # Update the server mode for the next loop
                    if last_polled_server_mode != self.scraper_server.mode:
                        Logger.console_log(str(self) + " has noticed a change in scraper server mode to " +
                                           str(self.scraper_server.mode) + " the time is " +
                                           str(datetime.now()), status=Logger.LogStatus.COMMUNICATION)
                        # server_mode change.  Time to retrieve processing data.
                        if self.scraper_server.mode == Scraper.ServerModes.SURVEY_MARKET:
                            # Survey the market, it must be closed.
                            self.scraper_server.executive_lock.acquire()
                            ticker_survey_list = self.ticker_survey_list
                            self.scraper_server.executive_lock.release()
                        elif self.scraper_server.mode == Scraper.ServerModes.RETRIEVE_DATA:
                            # Stock market is open schedule
                            self.scraper_server.executive_lock.acquire()
                            ticker_monitor_list = self.ticker_monitor_list
                            self.scraper_server.executive_lock.release()

                    # Update the server mode
                    last_polled_server_mode = self.scraper_server.mode
            except (KeyboardInterrupt, SystemExit):
                self.scraper_server.mode_lock.acquire()
                self.scraper_server.mode = Scraper.ServerModes.SHUT_DOWN
                self.scraper_server.mode_lock.release()

    class FileHandler:
        @staticmethod
        def store_tickers(tickers: dict, relative_path_correction: str = "") -> None:
            """
            :param relative_path_correction:
            :param tickers:
            :return:
            """
            ticker_directory = os.getcwd() + os.sep + relative_path_correction + "Data" + os.sep + "tickers" + os.sep

            for ticker_starting_letter in tickers.keys():
                Scraper.FileHandler.store_valid_ticker(ticker_data=tickers[ticker_starting_letter],
                                                       ticker_file_path=ticker_directory + ticker_starting_letter +
                                                                        '.json')

        @staticmethod
        def store_valid_ticker(ticker_data: list, ticker_file_path: str):
            """
            :param ticker_data:
            :param ticker_file_path:
            :return:
            """
            with open(ticker_file_path, "w+") as ticker_letter_file:
                json.dump(obj=ticker_data, fp=ticker_letter_file)

        @staticmethod
        def remove_invalid_ticker(ticker: str, relative_path_correction: str = "") -> None:
            ticker_directory = os.getcwd() + os.sep + relative_path_correction + "Data" + os.sep + "tickers" + os.sep
            ticker_starting_letter = ticker[0]

            # Load old tickers and remove from list
            ticker_data = Scraper.FileHandler.load_tickers(ticker_starting_letter=ticker_starting_letter,
                                                           relative_path_correction=relative_path_correction)
            ticker_data.remove(ticker)

            # Store new list of tickers
            Scraper.FileHandler.store_valid_ticker(ticker_data=ticker_data, ticker_file_path=ticker_directory +
                                                                                             ticker_starting_letter +
                                                                                             '.json')

        @staticmethod
        def load_tickers(ticker_starting_letter: str, relative_path_correction: str = "") -> list:
            """
            :param ticker_starting_letter:
            :param relative_path_correction:
            :return:
            """
            ticker_directory = os.getcwd() + os.sep + relative_path_correction + "Data" + os.sep + "tickers" + os.sep

            with open(ticker_directory + ticker_starting_letter + '.json', 'r') as ticker_file:
                return list(json.load(fp=ticker_file))

        @staticmethod
        def load_all_tickers(relative_path_correction: str = "") -> list:
            """
            :param relative_path_correction:
            :return:
            """
            ticker_list = []

            ticker_directory = os.getcwd() + os.sep + relative_path_correction + "Data" + os.sep + "tickers" + os.sep
            ticker_file_names = [file for file in os.listdir(ticker_directory) if
                                 os.path.isfile(os.path.join(ticker_directory, file))]

            for file_name in ticker_file_names:
                with open(os.path.join(ticker_directory, file_name)) as ticker_file:
                    ticker_list.extend(json.load(fp=ticker_file))

            return ticker_list

        @staticmethod
        def add_ticker_to_tickers(ticker: str, relative_path_correction: str) -> None:
            """
            :param ticker:
            :param relative_path_correction:
            :return:
            """
            ticker_file_path = os.getcwd() + os.sep + relative_path_correction + "Data" + os.sep + "tickers" + os.sep + \
                               ticker[0] + '.json'

            # Retrieve Ticker Data
            current_ticker_data = Scraper.FileHandler.load_tickers(ticker_starting_letter=ticker[:1],
                                                                   relative_path_correction=relative_path_correction)

            # update current ticker data
            current_ticker_data.append(ticker)

            # log new ticker data
            Scraper.FileHandler.store_valid_ticker(ticker_data=current_ticker_data, ticker_file_path=ticker_file_path)

        @staticmethod
        def get_last_ticker_surveyed(ticker_starting_letter: str, relative_path_correction: str = "") -> Union[
            str, None]:
            """
            :param ticker_starting_letter:
            :param relative_path_correction:
            :return:
            """
            # Get last surveyed ticker
            previous_ticker_list = Scraper.FileHandler.load_tickers(ticker_starting_letter=ticker_starting_letter,
                                                                    relative_path_correction=relative_path_correction)

            if len(previous_ticker_list) > 0:
                return previous_ticker_list[-1]
            else:
                return None

        @staticmethod
        def store_ticker_data(ticker: str, data: DataFrame, relative_path_correction: str = "") -> None:
            """
            :param ticker:
            :param data:
            :param relative_path_correction:
            :return:
            """
            ticker_data_file_path = os.getcwd() + os.sep + relative_path_correction + "Data" + os.sep + "ticker_data" \
                                    + os.sep + ticker + "_data.pkl"

            # Determine if ticker data already exists.
            if os.path.isfile(ticker_data_file_path):
                # File does exist. Must open then append.
                old_data = Scraper.FileHandler.retrieve_ticker_data(ticker=ticker,
                                                                    relative_path_correction=relative_path_correction)
                old_data.append(data)
                old_data.to_pickle(ticker_data_file_path)
            else:
                # File does not exist. Easy street. Create.
                data.to_pickle(ticker_data_file_path)

        @staticmethod
        def retrieve_ticker_data(ticker: str, relative_path_correction: str):
            """
            :param ticker:
            :param relative_path_correction:
            :return:
            """
            ticker_data_file_path = os.getcwd() + os.sep + relative_path_correction + "Data" + os.sep + "ticker_data" \
                                    + os.sep + ticker + "_data.pkl"
            return read_pickle(ticker_data_file_path)

    class WebInterface:
        @staticmethod
        def get_price(ticker: str) -> float:
            """
            :param ticker: Stock ticker.
            :return: Price in dollars as floating point.
            """
            # Build URL
            source_url = "https://finance.yahoo.com/quote/"
            source_url += ticker
            source_url += "?p="
            source_url += ticker
            source_url += "&.tsrc=fin-srch"

            # Open URL using urllib
            web_page = urlopen(source_url)

            # Use BeautifulSoup to parse url page
            soup = BeautifulSoup(web_page, "html.parser")

            # Get Current Price
            current_price = soup.find("div", {"class": "My(6px) Pos(r) smartphone_Mt(6px)"}).find("span").text

            return float(current_price)

        @staticmethod
        def get_current_ticker_data(ticker: str) -> DataFrame:
            """
            :param ticker: Stock ticker.
            :return: Pandas dataframe representing the current ticker data with columns ["timestamp", "price", "previous_close", "open", "bid", "ask", "volume", "avg_volume"]
            """
            # Build URL
            source_url = "https://finance.yahoo.com/quote/"
            source_url += ticker
            source_url += "?p="
            source_url += ticker
            source_url += "&.tsrc=fin-srch"

            # Open URL using urllib
            web_page = urlopen(source_url)

            # Use BeautifulSoup to parse url page
            soup = BeautifulSoup(web_page, "html.parser")

            # Get Current Price
            current_price = soup.find("div", {"class": "My(6px) Pos(r) smartphone_Mt(6px)"}).find("span").text

            # Get Chart Patter table
            chart_patter_table = soup.find("div", {
                "class": "D(ib) W(1/2) Bxz(bb) Pend(12px) Va(t) ie-7_D(i) smartphone_D(b) smartphone_W(100%) smartphone_Pend(0px) smartphone_BdY smartphone_Bdc($seperatorColor)"})

            # Get Previous Close
            previous_close, previous_open, bid, ask, volume, avg_volume = \
                [row.text for row in chart_patter_table.find_all("span", {"class": "Trsdu(0.3s)"})]

            data = array(
                [datetime.now(), current_price, previous_close, previous_open, bid, ask, volume, avg_volume]).reshape(
                (1, -1))
            labels = ["timestamp", "price", "previous_close", "open", "bid", "ask", "volume", "avg_volume"]

            df = DataFrame(data=data, columns=labels)
            df.set_index('timestamp', inplace=True)

            return df

    @staticmethod
    def survey_ticker(thread: Thread, ticker: str) -> bool:
        """
        Uses Scraper.get_current_ticker_data to survey the given ticker string.  The result is returned.
        :param thread: A Scraper.WorkerThread responsible for carrying out the survey.
        :param ticker: Stock ticker.
        :return: Boolean denoting rather or not the ticker was successfully scraped during the survey.
        """
        try:
            data = Scraper.WebInterface.get_current_ticker_data(ticker=ticker)

            if None in data:
                return False
            else:
                Logger.console_log("Successful scraping of ticker " + ticker + " from " + str(thread),
                                   Logger.LogStatus.SUCCESS)
                return True
        except Exception as e:
            return False

    @staticmethod
    def get_ticker_survey_list(starting_letter: str, last_ticker_surveyed: Union[str, None]) -> list:
        """
        :param starting_letter:
        :param last_ticker_surveyed:
        :return:
        """
        three_letter_tickers = ["".join(lst) for lst in product(ascii_uppercase, repeat=3) if lst[0] == starting_letter]
        four_letter_tickers = ["".join(lst) for lst in product(ascii_uppercase, repeat=4) if lst[0] == starting_letter]
        five_letter_tickers = ["".join(lst) for lst in product(ascii_uppercase, repeat=5) if lst[0] == starting_letter]
        possible_tickers = three_letter_tickers + four_letter_tickers + five_letter_tickers

        if last_ticker_surveyed is None:
            return possible_tickers
        else:
            return possible_tickers[possible_tickers.index(last_ticker_surveyed) + 1:]


def is_datetime_weekday(current_time: datetime):
    return current_time.isoweekday() in range(1, 6)


if __name__ == "__main__":
    test_server = Scraper(relative_path_correction=".." + os.sep, data_refresh_rate=1800)
    test_server.run()