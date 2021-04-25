"""Logger.py: Python Logger tested on both Linux and Windows operating systems that provides file logging and console log
   operations."""
from __future__ import annotations

__author__ = "Jacob Taylor Casasdy"
__email__ = "jacobtaylorcassady@outlook.com"

from datetime import datetime
from enum import Enum
from platform import system
from typing import Union
from os import getcwd, makedirs
from os.path import sep, abspath
from termcolor import colored

class Logger(object):
    """"""
    def __init__(self, file_log: bool = True, log_location: Union[str, None] = None) -> None:
        """Constructor.

        Args:
            file_log (bool, optional): [description]. Defaults to True.
            log_location (Union[str, None], optional): [description]. Defaults to None."""
        self.file_log: bool = file_log

        if file_log:
            if log_location is None:
                self.log_location = getcwd() + sep + ".." + sep + "Logs" + sep + datetime.now().strftime('%Y_%m_%d_%H_%M_%S_%f')[:-3] + ".log"
            else:
                self.log_location = log_location

            # Ensure log directory exists
            makedirs(abspath(self.log_location), exist_ok=True)

    def log(self, message: str, message_type: MESSAGE_TYPE) -> None:
        """Logs a message to a file and to the console given a status.

        Args:
            message (str): [description]
            status (LogStatus): [description]"""
        if self.file_log:
            Logger.log_to_file(log_file_location=self.log_location,
                               message=message, message_type=message_type)
        Logger.console_log(message=message, message_type=message_type)

    @staticmethod
    def log_to_file(log_file_location: str, message: str, message_type: MESSAGE_TYPE) -> None:
        """[summary]

        Args:
            log_file_location (str): [description]
            message (str): [description]
            status (LogStatus): [description]"""
        with open(log_file_location, 'a+') as log_file:
            log_file.write(datetime.now().strftime('%H:%M:%S.%f')[:-3] + ' - [{}]'.format(str(message_type)) + ' - ' + message + '\n')

    def verbose_console_log(verbose: bool, message: str, message_type: MESSAGE_TYPE) -> None:
        """[summary]

        Args:
            verbose (bool): [description]
            message (str): [description]
            message_type (MESSAGE_TYPE): [description]"""
        if verbose:
            Logger.console_log(message=message, message_type=message_type)

    @staticmethod
    def console_log(message: str, message_type: MESSAGE_TYPE) -> None:
        """[summary]

        Args:
            message (str): [description]
            status (LogStatus): [description]"""
        system_platform = system()
        time_string = datetime.now().strftime('%H:%M:%S.%f')[:-3]

        if system_platform == 'Windows':

            if message_type == Logger.MESSAGE_TYPE.SUCCESS:
                print(colored(text=time_string, color="white"), colored(text=message, color="green"))
            elif message_type == Logger.MESSAGE_TYPE.FAIL:
                print(colored(text=time_string, color="white"), colored(text=message, color="red"))
            elif message_type == Logger.MESSAGE_TYPE.STATUS:
                print(colored(text=time_string, color="white"), colored(text=message, color="cyan"))
            elif message_type == Logger.MESSAGE_TYPE.MINOR_FAIL:
                print(colored(text=time_string, color="white"), colored(text=message, color="magenta"))
            elif message_type == Logger.MESSAGE_TYPE.WARNING:
                print(colored(text=time_string, color="white"), colored(text=message, color="yellow"))
            else:
                print(colored(text=time_string, color="white"), colored(text=message, color="red"))
        else:
            from colorama import Fore

            if message_type == Logger.MESSAGE_TYPE.SUCCESS:
                print(Fore.WHITE + time_string + Fore.GREEN + ' ' + message)  #SUCCESS
            elif message_type == Logger.MESSAGE_TYPE.FAIL:
                print(Fore.WHITE + time_string + Fore.RED + ' ' + message)   #FAIL
            elif message_type == Logger.MESSAGE_TYPE.STATUS:
                print(Fore.WHITE + time_string + Fore.CYAN + ' ' + message)
            elif message_type == Logger.MESSAGE_TYPE.MINOR_FAIL:
                print(Fore.WHITE + time_string + Fore.LIGHTRED_EX + ' ' + message)  #Minor fail
            elif message_type == Logger.MESSAGE_TYPE.WARNING:
                print(Fore.WHITE + time_string + Fore.YELLOW + ' ' + message)
            else:
                print(Fore.WHITE + time_string + Fore.RED + ' INVALID LOG FORMAT. Please check int value.')

    class MESSAGE_TYPE(Enum):
        """[summary]"""
        SUCCESS = "SUCCESS"
        FAIL = "FAIL"
        STATUS = "STATUS"
        MINOR_FAIL = "MINOR_FAIL"
        WARNING = "WARNING"

        def __str__(self) -> str:
            return self.value

if __name__ == "__main__":
    for message_type in list(Logger.MESSAGE_TYPE):
        Logger.console_log(message="[" + str(message_type) + "] Hello World.", message_type=message_type)
