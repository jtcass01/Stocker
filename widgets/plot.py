#/usr/bin/env python
"""plot.py:"""

__author__ = "Jacob T. Cassady"
__email__ = "jacobtaylorcassady@outlook.com"

from typing import Union, Optional, Dict, Any

from PyQt5.QtCore import Qt, QTimer, QMutex
from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import QCheckBox, QFrame, QVBoxLayout, QWidget, QSplitter, QSpacerItem, QSizePolicy
from pyqtgraph import LegendItem, PlotWidget, DateAxisItem, mkPen, mkBrush

from holdings import Holdings

class PlotDisplay(QSplitter):
    """[summary]"""

    def __init__(self, stocker: object) -> None:
        """Constructor.

        Args:
            parent (Optional[QWidget]): [description]
            flags (Union[Qt.WindowFlags, Qt.WindowType]): [description]"""
        QSplitter.__init__(self, Qt.Horizontal)

        self.stocker = stocker
        self.data_lines: Dict[Any] = {}
        self.plot: PlotWidget = PlotDisplay.Plot(parent=self)
        self.plot_settings_frame: QFrame = PlotDisplay.PlotSettingsFrame(parent=self, stocker=self.stocker)
        self.colors = {
            "blue": QColor(0, 0, 255, 255),
            "green": QColor(0, 255, 0, 255),
            "red": QColor(255, 0, 0, 255),
            "cyan": QColor(0, 255, 255, 255),
            "magenta": QColor(255, 0, 255, 255),
            "yellow": QColor(255, 255, 0, 255),
            "dark-gray": QColor(150, 150, 150, 255),
            "light-gray": QColor(200, 200, 200, 255),
            "gray": QColor(100, 100, 150, 255),
            "orange": QColor(255, 165, 0, 255),
            "salmon": QColor(250, 128, 114, 255),
            "violet": QColor(238, 130, 238, 255),
            "aqua-marine": QColor(127, 255, 212, 255)
        }
        self.color_iterator = 0
        self.mutex = QMutex()
        self.update_timer = QTimer()

        self.initUI()
        self.setCallbacks()

        self.update_timer.setInterval(300)
        self.update_timer.start()

    def initUI(self) -> None:
        """Initializes user interface."""
        self.addWidget(self.plot)
        self.addWidget(self.plot_settings_frame)

    def setCallbacks(self) -> None:
        for check_box_name, check_box in self.plot_settings_frame.check_boxes.items():
            check_box.stateChanged.connect(self.plot_equities)

        self.update_timer.timeout.connect(self.update_plots)

    def update_plots(self) -> None:
        if self.mutex.tryLock(0):
            for data_line_name, data_line in self.data_lines.items():
                self.stocker.holdings.lock.acquire()
                x = self.stocker.holdings.get_times(holding_type=Holdings.HOLDING_TYPE(data_line_name))
                y = self.stocker.holdings.calculate_holding_equities(holding_type=Holdings.HOLDING_TYPE(data_line_name), times=x)
                self.stocker.holdings.lock.release()
                data_line.setData(x, y)
            self.mutex.unlock()

    def plot_equities(self) -> None:
        for check_box_name, check_box in self.plot_settings_frame.check_boxes.items():
            if check_box.isChecked():
                if check_box_name not in self.data_lines.keys():
                    holding_type = Holdings.HOLDING_TYPE(check_box_name)
                    holdings: Holdings = self.stocker.holdings

                    holdings.lock.acquire()
                    x = holdings.get_times(holding_type=holding_type)
                    y = holdings.calculate_holding_equities(holding_type=holding_type, times=x)
                    holdings.lock.release()

                    self.mutex.lock()
                    self.data_lines[check_box_name] = self.plot.plot(x=x, y=y, name=check_box_name,
                                                                     pen=mkPen(color=self.colors[list(self.colors.keys())[self.color_iterator]],
                                                                               width=4))
                    self.mutex.unlock()
                    self.color_iterator += 1
                    self.color_iterator %= len(self.colors.keys())
            else:
                if check_box_name in self.data_lines.keys():
                    self.mutex.lock()
                    self.plot.removeItem(self.data_lines[check_box_name])
                    del self.data_lines[check_box_name]
                    self.mutex.unlock()

    class Plot(PlotWidget):
        """[summary]"""

        def __init__(self, parent: Optional[QWidget] = None):
            """Constructor."""
            PlotWidget.__init__(self, axisItems={"bottom": DateAxisItem()}, parent=parent)
            self.legend: LegendItem = self.addLegend()
            self.showGrid(x=True, y=True)

    class PlotSettingsFrame(QFrame):
        def __init__(self, stocker: object, parent: Optional[QWidget] = None, 
                    flags: Union[Qt.WindowFlags, Qt.WindowType] = None) -> None:
            """Constructor.

            Args:
                parent (Optional[QWidget]): [description]
                flags (Union[Qt.WindowFlags, Qt.WindowType]): [description]"""
            QFrame.__init__(self, parent=parent)

            self.stocker: object = stocker
            self.check_boxes: Dict[str, QCheckBox] = PlotDisplay.PlotSettingsFrame.initailize_check_boxes()

            self.initUI()

        @staticmethod
        def initailize_check_boxes() -> Dict[str, QCheckBox]:
            check_boxes = {}

            for holding in list(Holdings.HOLDING_TYPE):
                check_boxes[holding.value] = QCheckBox()
                check_boxes[holding.value].setText(holding.value) 

            return check_boxes

        def initUI(self):
            """initializes user interface."""
            layout = QVBoxLayout()

            for check_box_name, check_box in self.check_boxes.items():
                layout.addWidget(check_box)

            verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding) 
            layout.addItem(verticalSpacer)

            self.setLayout(layout)
