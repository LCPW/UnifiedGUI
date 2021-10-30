from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

import os


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
        self.button_add_decoder.setText("Add Decoder")
        self.button_add_decoder.setIcon(QIcon('./Views/Icons/add.png'))
        self.button_add_decoder.clicked.connect(self.add_decoder)
        self.toolbar.addWidget(self.button_add_decoder)

        self.button_remove_decoder = QToolButton()
        self.button_remove_decoder.setText("Remove Decoder")
        self.button_remove_decoder.setIcon(QIcon('./Views/Icons/remove.png'))
        self.button_remove_decoder.setEnabled(False)
        self.button_remove_decoder.clicked.connect(self.remove_decoder)
        self.toolbar.addWidget(self.button_remove_decoder)

        self.button_start_decoder = QToolButton()
        self.button_start_decoder.setText("Start Decoder")
        self.button_start_decoder.setIcon(QIcon('./Views/Icons/play.png'))
        self.button_start_decoder.setEnabled(False)
        self.button_start_decoder.clicked.connect(self.start_decoder)
        self.toolbar.addWidget(self.button_start_decoder)

        self.button_stop_decoder = QToolButton()
        self.button_stop_decoder.setText("Stop Decoder")
        self.button_stop_decoder.setIcon(QIcon('./Views/Icons/stop.png'))
        self.button_stop_decoder.setEnabled(False)
        self.button_stop_decoder.clicked.connect(self.stop_decoder)
        self.toolbar.addWidget(self.button_stop_decoder)

        label = QLabel("Decoder")
        label.setFont(FONT_BIG)
        label.setAlignment(Qt.AlignTop | Qt.AlignHCenter)

        self.layout.addWidget(label)
        self.layout.addWidget(self.toolbar)
        self.layout.addStretch(1)

        self.setLayout(self.layout)

    def add_decoder(self):
        decoder_type, ok = QInputDialog.getItem(self, "Add Decoder", "Decoder type", self.available_decoders, 0, False)
        if ok:
            self.main_view.controller.add_decoder(decoder_type)

    def remove_decoder(self):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Warning)
        icon_msg = self.style().standardIcon(getattr(QStyle, 'SP_MessageBoxWarning'))
        msg.setWindowIcon(icon_msg)
        msg.setText("Are you sure you want to remove the decoder?")
        msg.setInformativeText("You can still view and export the current data,"
                               " but it is not possible to restart the plot without clearing all current data")
        msg.setWindowTitle("Remove decoder?")
        msg.setStandardButtons(QMessageBox.Yes | QMessageBox.Cancel)
        ret = msg.exec()
        if ret == QMessageBox.Yes:
            self.main_view.controller.remove_decoder()

    def start_decoder(self):
        self.main_view.controller.start_decoder()

    def stop_decoder(self):
        # TODO: Confirmation window
        self.main_view.controller.stop_decoder()

    def decoder_added(self, decoder_name):
        # TODO: Add information about decoder and receivers in the GUI
        self.label = QLabel(decoder_name)
        self.layout.addWidget(self.label)

        self.button_add_decoder.setEnabled(False)
        self.button_remove_decoder.setEnabled(True)
        self.button_start_decoder.setEnabled(True)
        self.button_stop_decoder.setEnabled(False)

    def decoder_removed(self):
        self.label.deleteLater()

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