from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
import os
import copy

from Views import MessageBoxes


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
        # TODO: Lines
        # Position for potential grid layout
        # self.positions = ['header', 'subheader', 'toolbar', 'parameters_label, parameters, symbol_values_label, symbol_values, sequence_label, sequence']

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

        self.button_parameters = QToolButton()
        self.button_parameters.setToolTip("Edit Parameters")
        self.button_parameters.setIcon(QIcon('./Views/Icons/tune.png'))
        self.button_parameters.setEnabled(False)
        self.button_parameters.clicked.connect(self.main_view.controller.edit_parameters)
        self.toolbar.addWidget(self.button_parameters)

        label = QLabel("Decoder")
        label.setObjectName("header")

        #label.setAlignment(Qt.AlignTop | Qt.AlignHCenter)

        self.label_subtitle = QLabel("No decoder selected")

        def line():
            line_ = QFrame()
            line_.setFrameShape(QFrame.HLine)
            line_.setFrameShadow(QFrame.Sunken)
            return line_

        self.layout.addWidget(label)
        self.layout.addWidget(self.label_subtitle)
        self.layout.addWidget(line())
        self.layout.addWidget(self.toolbar)
        self.layout.addWidget(line())
        self.layout.addStretch(1)

        self.setLayout(self.layout)

        self.label_symbol_values = None
        self.text_edit_symbol_values = None
        self.label_sequence = None
        self.text_edit_sequence = None
        self.label_parameters = None
        self.table_parameters = None

    def parameters_edited(self, parameter_values):
        for i in range(len(parameter_values)):
            value = list(parameter_values.values())[i]
            self.table_parameters.setItem(i, 1, QTableWidgetItem(str(value)))

    def add_decoder(self):
        decoder_type, ok = QInputDialog.getItem(self, "Add Decoder", "Decoder type", self.available_decoders, 0, False)
        if ok:
            self.main_view.controller.add_decoder(decoder_type)

    def remove_decoder(self):
        if MessageBoxes.warning(self.style(), "Remove decoder?", "Are you sure you want to remove the decoder?", "All data that has not been exported yet, cannot be recovered."):
            self.main_view.controller.remove_decoder()

    def start_decoder(self):
        # TODO: Allow for restarting after stopped
        self.main_view.controller.start_decoder()

    def stop_decoder(self):
        if MessageBoxes.warning(self.style(), "Stop decoder?", "Are you sure you want to stop the decoder?", "Once the decoder is stopped, no more new data can be shown."):
            self.main_view.controller.stop_decoder()

    def decoder_added(self, decoder_type, parameter_values):
        self.label_subtitle.setText(decoder_type)

        if parameter_values:
            self.label_parameters = QLabel("Parameter values")
            self.table_parameters = QTableWidget()
            self.table_parameters.setRowCount(len(parameter_values))
            self.table_parameters.setColumnCount(2)
            self.table_parameters.setHorizontalHeaderLabels(["Description", "Value"])
            # Table will fit the screen horizontally
            self.table_parameters.horizontalHeader().setStretchLastSection(True)
            self.table_parameters.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
            # TODO: Nochmal anschauen: https://doc.qt.io/qt-5/qtableview.html
            #self.table_parameters.verticalHeader().setStretchLastSection(True)
            self.table_parameters.verticalHeader().setSectionResizeMode(QHeaderView.Stretch)
            #self.table_parameters.resizeRowsToContents()
            for i in range(len(parameter_values)):
                description = list(parameter_values.keys())[i]
                value = parameter_values[description]
                self.table_parameters.setItem(i, 0, QTableWidgetItem(str(description)))
                self.table_parameters.setItem(i, 1, QTableWidgetItem(str(value)))
            self.button_parameters.setEnabled(True)

        self.label_symbol_values = QLabel("Symbol values")
        self.text_edit_symbol_values = QPlainTextEdit()
        self.text_edit_symbol_values.setReadOnly(True)

        self.label_sequence = QLabel("Decoded sequence")
        self.text_edit_sequence = QPlainTextEdit()
        self.text_edit_sequence.setReadOnly(True)

        if parameter_values:
            self.layout.addWidget(self.label_parameters)
            self.layout.addWidget(self.table_parameters)

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
        if self.label_parameters:
            self.label_parameters.deleteLater()
            self.label_parameters = None
            self.table_parameters.deleteLater()
            self.table_parameters = None

        self.button_add_decoder.setEnabled(True)
        self.button_remove_decoder.setEnabled(False)
        self.button_start_decoder.setEnabled(False)
        self.button_stop_decoder.setEnabled(False)
        self.button_parameters.setEnabled(False)

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