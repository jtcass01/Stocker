#/usr/bin/env python
"""cardano.py: """
from __future__ import annotations

__author__ = "Jacob T. Cassady"
__email__ = "jacobtaylorcassady@outlook.com"

# Built-in modules
from unittest import main, TestCase

class DaedalusWalletInterface(object):
    def __init__(self):
        pass


class Test_DaedalusWalletInterface(TestCase):
    def test_initialization(self):
        print("Starting test: Test_BinanceInterface.test_initialization")
        test_daedalus_wallet_interface: DaedalusWalletInterface = DaedalusWalletInterface()
        print("Test complete.")


if __name__ == "__main__":
    main()
