from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *


class EncoderView(QWidget):
    # TODO
    def __init__(self):
        super().__init__()

        layout = QVBoxLayout()
        label = QLabel("Encoder")
        label.setObjectName("header")
        layout.addWidget(label)
        self.setLayout(layout)