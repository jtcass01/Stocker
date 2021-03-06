"""Logger.py: Python Logger tested on both Linux and Windows operating systems that provides file logging and console log
   operations.  I use this in many of my projects; It only makes sense to give it its own repository."""
from __future__ import annotations

__author__ = "Jacob Taylor Casasdy"
__email__ = "jacobtaylorcassady@outlook.com"

from datetime import datetime
from enum import IntEnum
from platform import system
from typing import Union
from os import getcwd, makedirs
from os.path import sep, abspath


class Logger(object):
    """"""
    def __init__(self, file_log: bool = True, log_location: Union[str, None] = None) -> None:
        """Constructor.

        Args:
            file_log (bool, optional): [description]. Defaults to True.
            log_location (Union[str, None], optional): [description]. Defaults to None."""
        self.file_log = file_log

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

        if system_platform == 'Windows':
            from printy import printy

            if message_type == Logger.MESSAGE_TYPE.SUCCESS:
                printy((datetime.now().strftime('%H:%M:%S.%f')[:-3]) + '[n]' + ' ' + message + '@', predefined='w')  # SUCCESS
            elif message_type == Logger.MESSAGE_TYPE.FAIL:
                printy((datetime.now().strftime('%H:%M:%S.%f')[:-3]) + '[r]' + ' ' + message + '@', predefined='w')  # FAIL
            elif message_type == Logger.MESSAGE_TYPE.STATUS:
                printy((datetime.now().strftime('%H:%M:%S.%f')[:-3]) + '[c]' + ' ' + message + '@', predefined='w')
            elif message_type == Logger.MESSAGE_TYPE.MINOR_FAIL:
                printy((datetime.now().strftime('%H:%M:%S.%f')[:-3]) + '[r>]' + ' ' + message + '@', predefined='w') # Minor Fail
            elif message_type == Logger.MESSAGE_TYPE.WARNING:
                printy((datetime.now().strftime('%H:%M:%S.%f')[:-3]) + '[y]' + ' ' + message + '@', predefined='w')
            else:
                printy((datetime.now().strftime('%H:%M:%S.%f')[:-3]) + '[r]' + ' ' + 'INVALID LOG FORMAT. Please check int value.' + '@', predefined='w')
        else:
            from colorama import Fore

            if message_type == Logger.MESSAGE_TYPE.SUCCESS:
                print(Fore.WHITE + datetime.now().strftime('%H:%M:%S.%f')[:-3] + Fore.GREEN + ' ' + message)  #SUCCESS
            elif message_type == Logger.MESSAGE_TYPE.FAIL:
                print(Fore.WHITE + datetime.now().strftime('%H:%M:%S.%f')[:-3] + Fore.RED + ' ' + message)   #FAIL
            elif message_type == Logger.MESSAGE_TYPE.STATUS:
                print(Fore.WHITE + datetime.now().strftime('%H:%M:%S.%f')[:-3] + Fore.CYAN + ' ' + message)
            elif message_type == Logger.MESSAGE_TYPE.MINOR_FAIL:
                print(Fore.WHITE + datetime.now().strftime('%H:%M:%S.%f')[:-3] + Fore.LIGHTRED_EX + ' ' + message)  #Minor fail
            elif message_type == Logger.MESSAGE_TYPE.WARNING:
                print(Fore.WHITE + datetime.now().strftime('%H:%M:%S.%f')[:-3] + Fore.YELLOW + ' ' + message)
            else:
                print(Fore.WHITE + datetime.now().strftime('%H:%M:%S.%f')[:-3] + Fore.RED + ' INVALID LOG FORMAT. Please check int value.')

    class MESSAGE_TYPE(IntEnum):
        """[summary]

        Args:
            IntEnum ([type]): [description]"""
        SUCCESS = 1
        FAIL = 2
        STATUS = 3
        MINOR_FAIL = 4
        WARNING = 5


if __name__ == "__main__":
    Logger.console_log(message="Hello World.", message_type=Logger.MESSAGE_TYPE.SUCCESS)