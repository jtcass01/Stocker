#/usr/bin/env python
"""pie.py:"""
from __future__ import annotations

__author__ = "Jacob T. Cassady"
__email__ = "jacobtaylorcassady@outlook.com"

# 3rd party Modules
from PyQt5.QtWidgets import QMainWindow, QSplitter
from PyQt5.QtCore import Qt

from widgets.equity_pies import EquityPieFrame
from widgets.plot import PlotDisplay

class EquityTracker(QMainWindow):
    def __init__(self, stocker: object):
        QMainWindow.__init__(self)
        self.setWindowTitle("Equity Tracker Display")

        self.stocker = stocker

        self.initUI()
 
    def initUI(self) -> None:
        """Initializes user interface."""
        equity_pie_frame: EquityPieFrame = EquityPieFrame(stocker=self.stocker,
                                                          show_equity_split=True,
                                                          show_stock_split=True,
                                                          show_crypto_split=True)

        plot_frame: PlotDisplay = PlotDisplay(stocker=self.stocker)

        pie_plot_splitter = QSplitter(Qt.Horizontal)
        pie_plot_splitter.addWidget(equity_pie_frame)
        pie_plot_splitter.addWidget(plot_frame)

        self.setCentralWidget(pie_plot_splitter)

