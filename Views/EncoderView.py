from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *


class EncoderView(QWidget):
    def __init__(self):
        super().__init__()

        layout = QVBoxLayout()
        label = QLabel("Encoder")
        label.setObjectName("header")
        self.label_subtitle = QLabel("Not yet supported.")
        layout.addWidget(label)
        layout.addWidget(self.label_subtitle)
        layout.addStretch(1)
        self.setLayout(layout)