from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *


class ToolbarView(QToolBar):
    def __init__(self):
        super().__init__()
        self.setMovable(False)

        self.button_start = QToolButton()
        self.button_start.setText("Start")
        self.addWidget(self.button_start)