from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
import os

from Views import Warnings


# TODO: Refactor
# Bigger font for titles
FONT_BIG = QFont('MS Shell Dlg 2', 14, weight=QFont.Bold)


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

        self.layout = QVBoxLayout()

        self.toolbar = QToolBar()

        self.button_add_decoder = QToolButton()
        self.button_add_decoder.setToolTip("Add Decoder")
        self.button_add_decoder.setIcon(QIcon('./Views/Icons/add.png'))
        self.button_add_decoder.clicked.connect(self.add_decoder)
        self.toolbar.addWidget(self.button_add_decoder)

        self.button_remove_decoder = QToolButton()
        self.button_remove_decoder.setToolTip("Remove Decoder")
        self.button_remove_decoder.setIcon(QIcon('./Views/Icons/remove.png'))
        self.button_remove_decoder.setEnabled(False)
        self.button_remove_decoder.clicked.connect(self.remove_decoder)
        self.toolbar.addWidget(self.button_remove_decoder)

        self.button_start_decoder = QToolButton()
        self.button_start_decoder.setToolTip("Start Decoder")
        self.button_start_decoder.setIcon(QIcon('./Views/Icons/play.png'))
        self.button_start_decoder.setEnabled(False)
        self.button_start_decoder.clicked.connect(self.start_decoder)
        self.toolbar.addWidget(self.button_start_decoder)

        self.button_stop_decoder = QToolButton()
        self.button_stop_decoder.setToolTip("Stop Decoder")
        self.button_stop_decoder.setIcon(QIcon('./Views/Icons/stop.png'))
        self.button_stop_decoder.setEnabled(False)
        self.button_stop_decoder.clicked.connect(self.stop_decoder)
        self.toolbar.addWidget(self.button_stop_decoder)

        label = QLabel("Decoder")
        label.setFont(FONT_BIG)
        #label.setAlignment(Qt.AlignTop | Qt.AlignHCenter)

        self.label_subtitle = QLabel("No decoder selected")

        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)

        self.layout.addWidget(label)
        self.layout.addWidget(self.label_subtitle)
        self.layout.addWidget(line)
        self.layout.addWidget(self.toolbar)
        self.layout.addStretch(1)

        self.setLayout(self.layout)

    def add_decoder(self):
        decoder_type, ok = QInputDialog.getItem(self, "Add Decoder", "Decoder type", self.available_decoders, 0, False)
        if ok:
            self.main_view.controller.add_decoder(decoder_type)

    def remove_decoder(self):
        if Warnings.warning(self.style(), "Remove decoder?", "Are you sure you want to remove the decoder?", "All data that has not been exported yet, cannot be recovered."):
            self.main_view.controller.remove_decoder()

    def start_decoder(self):
        # TODO: Allow for restarting after stopped
        self.main_view.controller.start_decoder()

    def stop_decoder(self):
        if Warnings.warning(self.style(), "Stop decoder?", "Are you sure you want to stop the decoder?", "Once the decoder is stopped, no more new data can be shown."):
            self.main_view.controller.stop_decoder()

    def decoder_added(self, decoder_name):
        # TODO: Add information about decoder and receivers in the GUI
        self.label_subtitle.setText(decoder_name)

        self.label_symbol_values = QLabel("Symbol values")
        self.text_edit_symbol_values = QPlainTextEdit()
        self.text_edit_symbol_values.setReadOnly(True)

        self.label_sequence = QLabel("Decoded sequence")
        self.text_edit_sequence = QPlainTextEdit()
        self.text_edit_sequence.setReadOnly(True)

        self.layout.addWidget(self.label_symbol_values)
        self.layout.addWidget(self.text_edit_symbol_values)

        self.layout.addWidget(self.label_sequence)
        self.layout.addWidget(self.text_edit_sequence)

        self.button_add_decoder.setEnabled(False)
        self.button_remove_decoder.setEnabled(True)
        self.button_start_decoder.setEnabled(True)
        self.button_stop_decoder.setEnabled(False)

    def decoder_removed(self):
        self.label_subtitle.setText("")

        self.label_symbol_values.deleteLater()
        self.label_sequence.deleteLater()
        self.text_edit_symbol_values.deleteLater()
        self.text_edit_sequence.deleteLater()

        self.button_add_decoder.setEnabled(True)
        self.button_remove_decoder.setEnabled(False)
        self.button_start_decoder.setEnabled(False)
        self.button_stop_decoder.setEnabled(False)

    def decoder_started(self):
        self.button_add_decoder.setEnabled(False)
        self.button_remove_decoder.setEnabled(False)
        self.button_start_decoder.setEnabled(False)
        self.button_stop_decoder.setEnabled(True)

    def decoder_stopped(self):
        self.button_add_decoder.setEnabled(False)
        self.button_remove_decoder.setEnabled(True)
        self.button_start_decoder.setEnabled(False)
        self.button_stop_decoder.setEnabled(False)

    def update_symbol_values(self, symbol_values):
        # Convert list to string
        string = ""
        for s in symbol_values:
            string += str(s)

        self.text_edit_symbol_values.setPlainText(string)

    def update_sequence(self, sequence):
        self.text_edit_sequence.setPlainText(sequence)