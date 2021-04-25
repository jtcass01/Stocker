#/usr/bin/env python
"""time_util.py:"""

__author__ = "Jacob T. Cassady"
__email__ = "jacobtaylorcassady@outlook.com"

from threading import Event
from time import time, sleep
from datetime import datetime

def pseudo_realtime_timestep(epoch_start_time: float, timestep: float, precision_scalar: float = 1000):
    """[summary]

    Args:
        epoch_start_time (float): [description]
        timestep (float): [description]
        precision_scalar (float, optional): [description]. Defaults to 1000."""
    while epoch_start_time + timestep >= time():
        sleep(timestep/precision_scalar)

class Stocker_Event(Event):
    """[summary"""
    def __init__(self):
        """Constructor."""
        Event.__init__(self)

    def wait(self, timeout_ms: float, dt: float = 0.0001) -> bool:
        """[summary]

        Args:
            timeout_ms (float): [description]
            dt (float, optional): [description]. Defaults to 0.0001.

        Returns:
            bool: [description]"""
        start_time = datetime.now()

        while not self.is_set():
            wait_time_ms = (datetime.now() - start_time).total_seconds() * 1000.

            if wait_time_ms > timeout_ms:
                return False
            else:
                sleep(dt)
        return True
