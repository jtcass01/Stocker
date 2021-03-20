#/usr/bin/env python
"""Control.py: contains Control_Window class."""
from __future__ import annotations

__author__ = "Jacob T. Cassady"
__email__ = "jacobtaylorcassady@outlook.com"

# Built-in modules
from enum import IntEnum
from typing import Union
from datetime import datetime

# 3rd Party Modules
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QLabel, QMainWindow, QScrollArea, QTextEdit, QVBoxLayout, QWidget, QFrame, QMenu, QSpacerItem, QSizePolicy
from PyQt5.QtGui import QFontMetrics, QKeyEvent

class ControlWindow(QMainWindow):
    """[summary]"""
    TITLE = "Control Window"

    def __init__(self, stocker: object):
        """Constructor.

        Args:
            stocker (object): [description]"""
        QMainWindow.__init__(self)
        self.stocker = stocker

        self.log_scroll_area: QScrollArea = ControlWindow.LogScrollArea(control_window=self)
        self.command_text_edit = ControlWindow.SingleLineTextEdit(control_window=self)

        self.initUI()
        self.setCallbacks()

    def initUI(self) -> None:
        """Initializes User Interface"""
        self.setWindowTitle(ControlWindow.TITLE)

        control_window_layout = QVBoxLayout()
        control_window_widget = QWidget(self)

        command_frame: QFrame = ControlWindow.CommandFrame(control_window=self)

        control_window_layout.addWidget(self.log_scroll_area)
        control_window_layout.addWidget(command_frame)
        control_window_widget.setLayout(control_window_layout)

        self.setCentralWidget(control_window_widget)

    def setCallbacks(self) -> None:
        """Sets callback methods for all UI objects."""
        pass

    class Callbacks:
        @staticmethod
        def send_command(command: str, stocker: object, 
                         log_scroll_area: ControlWindow.LogScrollArea) -> None:
            """[summary]

            Args:
                command (str): [description]
                stocker (object): [description]
                log_text_edit (ControlWindow.Log_Text_Edit): [description]"""
            log_scroll_area.print(command, message_type=ControlWindow.LogScrollArea.MESSAGE_TYPE.USER)

    class LogScrollArea(QScrollArea):
        """[summary]"""
        def __init__(self, control_window: Union[ControlWindow, None] = None):
            """Constructor.

            Args:
                control_window (Union[ControlWindow, None], optional): [description]. Defaults to None."""
            QScrollArea.__init__(self, parent=control_window)

            self.log_layout = QVBoxLayout()

            self.initUI()

        def initUI(self):
            """[summary]"""
            self.setLayout(self.log_layout)

        def print(self, message: str, message_type: MESSAGE_TYPE) -> None:
            """[summary]

            Args:
                message (str): [description]"""
            message_label = ControlWindow.ColoredLabel(text=message,
                                                       color=message_type.get_color(),
                                                       parent=self)
            self.log_layout.addWidget(message_label)

        class MESSAGE_TYPE(IntEnum):
            """[summary]

            Args:
                IntEnum ([type]): [description]"""
            USER = 0
            SUCCESS = 1
            FAIL = 2
            STATUS = 3
            MINOR_FAIL = 4
            WARNING = 5

            def get_color(self) -> str:
                """[summary]

                Returns:
                    str: [description]"""
                if self == ControlWindow.LogScrollArea.MESSAGE_TYPE.SUCCESS:
                    return "green"
                elif self == ControlWindow.LogScrollArea.MESSAGE_TYPE.FAIL:
                    return "red"
                elif self == ControlWindow.LogScrollArea.MESSAGE_TYPE.STATUS:
                    return "cyan"
                elif self == ControlWindow.LogScrollArea.MESSAGE_TYPE.MINOR_FAIL:
                    return "lightred"
                elif self == ControlWindow.LogScrollArea.MESSAGE_TYPE.WARNING:
                    return "yellow"
                elif self == ControlWindow.LogScrollArea.MESSAGE_TYPE.USER:
                    return "white"
                else:
                    raise NotImplementedError

    class CommandFrame(QFrame):
        """[summary]"""
        def __init__(self, control_window: Union[ControlWindow, None] = None):
            """Constructor.

            Args:
                control_window (Union[Control_Window, None], optional): [description]. Defaults to None."""
            QFrame.__init__(self, parent=control_window)
            command_layout = QVBoxLayout()

            command_line_label = QLabel(self)
            command_line_label.setText("Command Line:")

            command_layout.addItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))
            command_layout.addWidget(command_line_label)
            command_layout.addWidget(control_window.command_text_edit)

            self.setLayout(command_layout)
            #self.setSizePolicy(QSizePolicy., QSizePolicy.MinimumExpanding)

    class ColoredLabel(QLabel):
        """[summary]"""
        def __init__(self, text: str, color: str, parent: Union[QWidget, None] = None):
            """Constructor.

            Args:
                text (str): [description]
                color (str): [description]
                parent (Union[QWidget, None], optional): [description]. Defaults to None."""
            QLabel.__init__(self, parent=parent)
            self.setText(str(datetime.now().strftime('%H:%M:%S.%f')[:-3]) + " <font color=\'" + color + "\'>" + text + "</font>")

    class SingleLineTextEdit(QTextEdit):
        """[summary]"""
        def __init__(self, control_window: Union[ControlWindow, None] = None):
            """Constructor."""
            QTextEdit.__init__(self, parent=control_window)
            self.control_window = control_window

            metrics = QFontMetrics(self.font())
            line_height = metrics.lineSpacing() + 1
            self.setFixedHeight(line_height)

        def keyPressEvent(self, event: QKeyEvent) -> None:
            """Overriden method.

            Args:
                event (QKeyEvent): [description]"""
            if event.key() in (Qt.Key_Enter, Qt.Key_Return):
                self.control_window.Callbacks.send_command(command=self.toPlainText(),
                                                           stocker=self.control_window.stocker,
                                                           log_scroll_area=self.control_window.log_scroll_area)
                self.setText("")
            super().keyPressEvent(event)
