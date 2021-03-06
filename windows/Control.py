from PyQt5.QtWidgets import QMainWindow

class Control_Window(QMainWindow):
    """[summary]"""
    WINDOW_TITLE = "Control Window"

    def __init__(self, stocker: object):
        """[summary]

        Args:
            stocker (object): [description]"""
        QMainWindow.__init__(self)
        self.stocker = stocker

        self.initUI()

        self.show()

    def initUI(self) -> None:
        """Initializes User Interface"""
        self.setWindowTitle(Control_Window.WINDOW_TITLE)

    def setCallbacks(self) -> None:
        """Sets callback methods for all UI objects."""
        pass
