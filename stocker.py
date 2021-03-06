#/usr/bin/env python
"""stocker.py:"""

__author__ = "Jacob T. Cassady"
__email__ = "jacobtaylorcassady@outlook.com"

# Built-in Modules
from argparse import ArgumentParser
from sys import argv, exit
from typing import Callable

# 3rd party Modules
from PyQt5.QtWidgets import QApplication, QMainWindow
from qdarkstyle import load_stylesheet

# Stocker Library Modules
from utilities.Logger import Logger
from windows.Control import Control_Window

class Stocker(object):
    """[summary]"""
    def __init__(self, verbose: bool = False):
        """Constructor.

        Args:
            verbose (bool, optional): [description]. Defaults to False."""
        self.verbose = verbose
        
        self.generated_windows = {}

        self.open_window(window_class=Control_Window)

    def open_window(self, window_class: Callable[[], QMainWindow]) -> None:
        """[summary]

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

if __name__ == "__main__":
    # Determine if in debug mode
    parser = ArgumentParser()
    parser.add_argument("--verbose", "-v", help="verbose mode", default=True, required=False)
    arguments = parser.parse_args()

    if arguments.verbose:
        Logger.console_log(message="Stocker is starting in verbose mode", message_type=Logger.MESSAGE_TYPE.STATUS)

    app = QApplication(argv)
    Stocker(verbose=arguments.verbose)
    app.setStyleSheet(load_stylesheet(qt_api='pyqt5'))
    exit_response = app.exec_()
    exit(exit_response)
