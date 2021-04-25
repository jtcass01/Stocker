#/usr/bin/env python
"""equity_pies.py:"""
from __future__ import annotations

__author__ = "Jacob T. Cassady"
__email__ = "jacobtaylorcassady@outlook.com"

# Built-in Modules
from typing import Dict

# 3rd party Modules
from PyQt5.QtWidgets import QFrame, QVBoxLayout, QVBoxLayout, QWidget
from PyQt5.QtChart import QChartView, QChart, QPieSeries, QPieSlice
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPainter

# Stocker modules
from holdings import Holdings

class EquityPieFrame(QFrame):
    def __init__(self, stocker: object, show_equity_split: bool = True, show_stock_split: bool = True,
                 show_crypto_split: bool = True):
        """Constructor.

        Args:
            stocker (object): [description]
            show_equity_split (bool, optional): [description]. Defaults to True.
            show_stock_split (bool, optional): [description]. Defaults to True.
            show_crypto_split (bool, optional): [description]. Defaults to True."""
        QFrame.__init__(self)

        self.stocker = stocker

        self.initUI(show_equity_split=show_equity_split, show_stock_split=show_stock_split,
                    show_crypto_split=show_crypto_split)
 
    def initUI(self, show_equity_split: bool, show_stock_split: bool,
               show_crypto_split: bool) -> None:
        """Initializes user interface."""
        main_layout = QVBoxLayout()

        if show_equity_split:
            equity_split_chart_view: EquityPieFrame.EquitySplitChartView = EquityPieFrame.EquitySplitChartView(holdings=self.stocker.holdings)
            main_layout.addWidget(equity_split_chart_view)

        if show_stock_split:
            stock_equity_chart_view: EquityPieFrame.PieChartView = EquityPieFrame.StockSplitChartView(holdings=self.stocker.holdings)
            main_layout.addWidget(stock_equity_chart_view)

        if show_crypto_split:
            crypto_equity_chart_view: EquityPieFrame.PieChartView = EquityPieFrame.CryptoSplitChartView(holdings=self.stocker.holdings)
            main_layout.addWidget(crypto_equity_chart_view)

        self.setLayout(main_layout)

    class PieChartView(QChartView):
        """[summary]"""

        def __init__(self, data: Dict[str, float], title: str):
            """Constructor.

            Args:
                data (Dict[str, float]): [description]
                title (str): [description]"""
            pie_chart: QChart = EquityPieFrame.PieChartView.PieChart(data=data,
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
                QChart.__init__(self)
                self.legend().hide()
                pie_series = EquityPieFrame.PieChartView.PieChart.PieSeries(data=data)
                self.addSeries(pie_series)
                self.createDefaultAxes()
                self.setAnimationOptions(QChart.SeriesAnimations)
                self.setTitle(title)
                self.legend().setVisible(True)
                self.legend().setAlignment(Qt.AlignRight)

                for data_key_index, data_key in enumerate(data.keys()):
                    self.legend().markers(pie_series)[data_key_index].setLabel(data_key)

            class PieSeries(QPieSeries):
                """[summary]"""

                def __init__(self, data: Dict[str, float]):
                    """Constructor.

                    Args:
                        data (Dict[str, float]): [description]"""
                    QPieSeries.__init__(self)
                    self.setLabelsVisible()
                    self.setLabelsPosition(QPieSlice.LabelInsideHorizontal)
                    for data_key, data_point in data.items():
                        self.append(data_key, data_point)

                    for slice in self.slices():
                        slice.setLabel("{:.2f}%".format(100*slice.percentage()))

    class EquitySplitChartView(PieChartView):
        TITLE: str = "Equity Split"

        def __init__(self, holdings: Holdings):
            """Constructor.

            Args:
                holdings (Holdings): [description]"""
            equities: Dict[str, float] = {}
            equities['stock'] = holdings.calculate_equity(holding_type=Holdings.HOLDING_TYPE.STOCK)
            equities['cryptocurrency'] = holdings.calculate_equity(holding_type=Holdings.HOLDING_TYPE.CRYPTOCURRENCY)
            equities['checking account'] = holdings.calculate_equity(holding_type=Holdings.HOLDING_TYPE.CHECKING)
            equities['USD in float'] = holdings.calculate_equity(holding_type=Holdings.HOLDING_TYPE.FLOATING_USD)

            EquityPieFrame.PieChartView.__init__(self, data=equities, title=EquityPieFrame.EquitySplitChartView.TITLE)

    class StockSplitChartView(PieChartView):
        TITLE: str = "Stock Split"

        def __init__(self, holdings: Holdings):
            """Constructor.

            Args:
                holdings (Holdings): [description]"""
            equities = {}

            for symbol, stock in holdings.stocks.items():
                equities[symbol] = stock.calculate_equity()

            EquityPieFrame.PieChartView.__init__(self, data=equities, title=EquityPieFrame.StockSplitChartView.TITLE)

    class CryptoSplitChartView(PieChartView):
        TITLE: str = "Crypto Split"

        def __init__(self, holdings: Holdings):
            """Constructor.

            Args:
                holdings (Holdings): [description]"""
            equities = {}

            for symbol, cryptocurrency in holdings.cryptocoins.items():
                equities[symbol] = cryptocurrency.calculate_equity()

            EquityPieFrame.PieChartView.__init__(self, data=equities, title=EquityPieFrame.CryptoSplitChartView.TITLE)

