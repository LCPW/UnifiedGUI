from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *


class DecoderView(QWidget):
    def __init__(self, main_view):
        super().__init__()

        self.main_view = main_view

        layout = QVBoxLayout()

        self.toolbar = QToolBar()

        self.button_add_decoder = QToolButton()
        self.button_add_decoder.setText("Add Decoder")
        self.button_add_decoder.clicked.connect(lambda: self.add_decoder("ExampleDecoder"))
        self.toolbar.addWidget(self.button_add_decoder)

        self.button_remove_decoder = QToolButton()
        self.button_remove_decoder.setText("Remove Decoder")
        self.button_remove_decoder.setEnabled(False)
        self.button_remove_decoder.clicked.connect(self.remove_decoder)
        self.toolbar.addWidget(self.button_remove_decoder)

        label = QLabel("Decoder")
        layout.addWidget(label)

        layout.addWidget(self.toolbar)
        self.setLayout(layout)

    def add_decoder(self, decoder_type):
        self.main_view.add_decoder(decoder_type)
        self.button_add_decoder.setEnabled(False)
        self.button_remove_decoder.setEnabled(True)

    def remove_decoder(self):
        self.main_view.remove_decoder()
        self.button_remove_decoder.setEnabled(False)
        self.button_add_decoder.setEnabled(True)
