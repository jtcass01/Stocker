#/usr/bin/env python
"""prices.py:"""

__author__ = "Jacob T. Cassady"
__email__ = "jacobtaylorcassady@outlook.com"

from threading import Thread
from time import time

from StatusLogger import Logger, Message

from utilities.time_util import pseudo_realtime_timestep

class PriceChecker(Thread):
    def __init__(self, stocker: object, verbose: bool = False, rate: float = 1./90.) -> None:
        Thread.__init__(self=self)
        self.verbose = verbose
        self.stocker = stocker
        self.rate = rate

    def run(self) -> None:
        self.running = True
        Logger.verbose_console_log(verbose=self.verbose,
                                   message=str(type(self)) + " is running...",
                                   message_type=Message.MESSAGE_TYPE.STATUS)

        while self.running:
            epoch_start_time = time()
            self.stocker.holdings.update(binance_account = self.stocker.binance_account, 
                                         coinbase_account = self.stocker.coinbase_account, 
                                         verbose = self.stocker.verbose)
            pseudo_realtime_timestep(epoch_start_time=epoch_start_time,
                                     timestep=1/self.rate)

    def stop(self) -> None:
        self.running = False
        Logger.verbose_console_log(verbose=self.verbose,
                                   message=str(type(self)) + " is stopping...",
                                   message_type=Message.MESSAGE_TYPE.STATUS)
