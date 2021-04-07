#/usr/bin/env python
"""pie.py:"""
from __future__ import annotations

__author__ = "Jacob T. Cassady"
__email__ = "jacobtaylorcassady@outlook.com"

# Built-in Modules
from sys import argv, exit
from typing import Dict

# 3rd party Modules
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QVBoxLayout, QWidget
from PyQt5.QtChart import QChartView, QChart, QPieSeries, QPieSlice
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPainter
from qdarkstyle import load_stylesheet

# Stocker modules
from interfaces.stock import get_stock_price

class PieDisplay(QMainWindow):
    def __init__(self, stocker: object):
        QMainWindow.__init__(self)
        self.setWindowTitle("Pie Display")

        self.stocker = stocker

        self.initUI()
 
    def initUI(self) -> None:
        """Initializes user interface."""
        main_widget = QWidget()
        main_layout = QVBoxLayout()

        equity_split_chart_view: PieDisplay.PieChartView = self.initialize_equity_split_chart()
        stock_equity_chart_view: PieDisplay.PieChartView = self.initialize_stock_equity_chart()
        crypto_equity_chart_view: PieDisplay.PieChartView = self.initialize_crypto_equity_chart()

        main_layout.addWidget(equity_split_chart_view)
        main_layout.addWidget(stock_equity_chart_view)
        main_layout.addWidget(crypto_equity_chart_view)
        main_widget.setLayout(main_layout)

        self.setCentralWidget(main_widget)

    def initialize_equity_split_chart(self) -> PieDisplay.PieChartView:
        """[summary]

        Returns:
            PieDisplay.EquitySplitChart: [description]"""
        equities: Dict[str, float] = {}
        equities['stock'] = self.stocker.calculate_stock_equity()
        equities['crypto'] = self.stocker.calculate_crypto_equity()

        return PieDisplay.PieChartView(data=equities, title="Equity Split")

    def initialize_stock_equity_chart(self) -> PieDisplay.PieChartView:
        stock_holdings = self.stocker.holdings['stocks']
        equities = {}

        for symbol, data in stock_holdings.items():
            equities[symbol] = data['quantity'] * get_stock_price(symbol=symbol)

        return PieDisplay.PieChartView(data=equities, title="Stock Holdings")

    def initialize_crypto_equity_chart(self) -> PieDisplay.PieChartView:
        crypto_holdings = self.stocker.holdings['crypto']
        coin_prices = self.stocker.binance_interface.get_prices(symbols=list(crypto_holdings.keys()))
        equities = {}

        for symbol, data in crypto_holdings.items():
            equities[symbol] = data['quantity'] * coin_prices[symbol]

        return PieDisplay.PieChartView(data=equities, title="Crypto Holdings")


    class PieChartView(QChartView):
        """[summary]"""

        def __init__(self, data: Dict[str, float], title: str):
            """Constructor.

            Args:
                data (Dict[str, float]): [description]
                title (str): [description]"""
            pie_chart: QChart = PieDisplay.PieChartView.PieChart(data=data,
                                                                 title=title)
            QChartView.__init__(self, pie_chart)
            self.setRenderHint(QPainter.Antialiasing)

        class PieChart(QChart):
            """[summary]"""

            def __init__(self, data: Dict[str, float], title: str):
                """Constructor.

                Args:
                    data (Dict[str, float]): [description]
                    title (str): [description]"""
                pie_series = QPieSeries()
                pie_series.setLabelsVisible()
                pie_series.setLabelsPosition(QPieSlice.LabelInsideHorizontal)
                for data_key, data_point in data.items():
                    pie_series.append(data_key, data_point)

                QChart.__init__(self)
                self.legend().hide()
                self.addSeries(pie_series)
                self.createDefaultAxes()
                self.setAnimationOptions(QChart.SeriesAnimations)
                self.setTitle(title)
                self.legend().setVisible(True)
                self.legend().setAlignment(Qt.AlignBottom)

                for slice in pie_series.slices():
                    slice.setLabel("{:.2f}%".format(100*slice.percentage()))

                for data_key_index, data_key in enumerate(data.keys()):
                    self.legend().markers(pie_series)[data_key_index].setLabel(data_key)


if __name__ == "__main__":
    app = QApplication(argv)
    pie_display = PieDisplay(stocker=None)
    pie_display.show()
    app.setStyleSheet(load_stylesheet(qt_api='pyqt5'))
    exit(app.exec_())
