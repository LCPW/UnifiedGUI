from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

import os


class DecoderView(QWidget):
    def __init__(self, main_view):
        super().__init__()

        self.main_view = main_view

        # Get a list of all available decoders by searching for .py files in the implementations folder
        self.available_decoders = []
        for file in os.listdir('./Models/Implementations/Decoders'):
            name, extension = os.path.splitext(file)
            if extension == '.py':
                self.available_decoders.append(name)

        layout = QVBoxLayout()

        self.toolbar = QToolBar()

        self.button_add_decoder = QToolButton()
        self.button_add_decoder.setText("Add Decoder")
        self.button_add_decoder.clicked.connect(self.add_decoder)
        self.toolbar.addWidget(self.button_add_decoder)

        self.button_remove_decoder = QToolButton()
        self.button_remove_decoder.setText("Remove Decoder")
        self.button_remove_decoder.setEnabled(False)
        self.button_remove_decoder.clicked.connect(self.remove_decoder)
        self.toolbar.addWidget(self.button_remove_decoder)

        self.button_start_decoder = QToolButton()
        self.button_start_decoder.setText("Start Decoder")
        self.button_start_decoder.setEnabled(True)
        self.button_start_decoder.clicked.connect(self.start_decoder)
        self.toolbar.addWidget(self.button_start_decoder)

        label = QLabel("Decoder")
        layout.addWidget(label)

        layout.addWidget(self.toolbar)
        self.setLayout(layout)

    def add_decoder(self):
        decoder_type, ok = QInputDialog.getItem(self, "Add Decoder", "Decoder type", self.available_decoders, 0, False)
        if ok:
            self.main_view.add_decoder(decoder_type)
            self.button_add_decoder.setEnabled(False)
            self.button_remove_decoder.setEnabled(True)

    def remove_decoder(self):
        self.main_view.remove_decoder()
        self.button_remove_decoder.setEnabled(False)
        self.button_add_decoder.setEnabled(True)

    def start_decoder(self):
        self.main_view.start_decoder()