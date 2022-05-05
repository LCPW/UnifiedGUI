from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from Utils import ViewUtils


class EncoderView(QWidget):
    def __init__(self, view):
        """
        Initializes the encoder view.
        :param view: Main window.
        """
        super().__init__()

        self.view = view

        self.resize(225, self.height())

        self.layout = QVBoxLayout()

        self.toolbar = QToolBar()

        self.button_add_encoder = QToolButton()
        self.button_add_encoder.setIcon(ViewUtils.get_icon('add'))
        self.button_add_encoder.setToolTip("Add encoder")
        self.button_add_encoder.setEnabled(True)
        self.button_add_encoder.clicked.connect(self.add_encoder)
        self.toolbar.addWidget(self.button_add_encoder)

        self.button_remove_encoder = QToolButton()
        self.button_remove_encoder.setIcon(ViewUtils.get_icon('remove'))
        self.button_remove_encoder.setToolTip("Remove encoder")
        self.button_remove_encoder.setEnabled(False)
        self.button_remove_encoder.clicked.connect(self.remove_encoder)
        self.toolbar.addWidget(self.button_remove_encoder)

        label = QLabel("Encoder")
        label.setObjectName("header")
        self.label_subtitle = QLabel("No encoder selected")

        self.layout.addWidget(label)
        self.layout.addWidget(self.label_subtitle)
        self.layout.addWidget(ViewUtils.line_h())
        self.layout.addWidget(self.toolbar)
        self.layout.addWidget(ViewUtils.line_h())
        self.layout.addStretch(1)
        self.setLayout(self.layout)

    def add_encoder(self):
        """
        Add a new encoder.
        """
        names = self.view.controller.get_available_encoders()

        encoder_type, ok = QInputDialog.getItem(self, "Add Decoder", "Decoder type", names, 0, False)
        if ok:
            self.view.controller.add_encoder(encoder_type)

    def cancel_transmission(self):
        """
        Cancels a running transmission.
        """
        self.view.controller.cancel_transmission()

    def encoder_added(self, encoder_info):
        """
        Do stuff when a new encoder is added.
        :param encoder_info: Information about encoder.
        """
        self.label_subtitle.setText(encoder_info['type'])

        parameter_values = encoder_info['parameter_values']
        self.has_parameters = True if parameter_values else False
        self.label_subtitle.setText(encoder_info['type'])

        if self.has_parameters:
            self.widget_label_parameters = QWidget()
            self.layout_label_parameters = QHBoxLayout()
            self.label_parameters = QLabel("Parameter values")
            self.label_parameters.setObjectName('subheader')
            self.button_parameters = QToolButton()
            self.button_parameters.setEnabled(True)
            self.button_parameters.setIcon(ViewUtils.get_icon('tune'))
            self.button_parameters.setToolTip("Edit parameters")
            self.button_parameters.clicked.connect(self.view.controller.edit_encoder_parameters)
            self.layout_label_parameters.addWidget(self.label_parameters)
            self.layout_label_parameters.addWidget(self.button_parameters)
            self.widget_label_parameters.setLayout(self.layout_label_parameters)

            self.table_parameters = QTableWidget()
            # Set non-editable
            self.table_parameters.setEditTriggers(QAbstractItemView.NoEditTriggers)
            self.table_parameters.setRowCount(len(parameter_values))
            self.table_parameters.setColumnCount(2)
            self.table_parameters.setHorizontalHeaderLabels(["Description", "Value"])
            # Table will fit the screen horizontally
            self.table_parameters.horizontalHeader().setStretchLastSection(True)
            self.table_parameters.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
            # https://doc.qt.io/qt-5/qtableview.html
            # self.table_parameters.verticalHeader().setStretchLastSection(True)
            # self.table_parameters.verticalHeader().setSectionResizeMode(QHeaderView.Stretch)
            self.table_parameters.verticalHeader().hide()
            # self.table_parameters.resizeRowsToContents()
            for i in range(len(parameter_values)):
                description = list(parameter_values.keys())[i]
                value = parameter_values[description]
                self.table_parameters.setItem(i, 0, QTableWidgetItem(str(description)))
                self.table_parameters.setItem(i, 1, QTableWidgetItem(str(value)))

        self.widget_sequence = QWidget()
        widget_sequence_layout = QHBoxLayout()

        self.label_sequence = QLabel("Sequence")
        self.label_sequence.setObjectName('subheader')
        self.text_edit_sequence = QTextEdit()
        self.button_load_sequence = QToolButton()
        self.button_load_sequence.setIcon(ViewUtils.get_icon('file_open'))
        self.button_load_sequence.setToolTip('Load sequence from file')
        self.button_load_sequence.clicked.connect(self.load_sequence)

        widget_sequence_layout.addWidget(self.label_sequence)
        widget_sequence_layout.addWidget(self.button_load_sequence)
        self.widget_sequence.setLayout(widget_sequence_layout)

        self.widget_encode = QWidget()
        widget_encode_layout = QHBoxLayout()
        self.button_encode_and_transmit = QPushButton("Encode&&Transmit")
        self.button_encode_and_transmit.setIcon(ViewUtils.get_icon('send'))
        self.button_encode_and_transmit.setToolTip('Encode sequence to symbol values and transmit')
        self.button_encode_and_transmit.clicked.connect(self.encode_and_transmit)

        self.button_encode = QPushButton("Encode")
        self.button_encode.setIcon(ViewUtils.get_icon('drive_file_move'))
        self.button_encode.setToolTip("Encode sequence to symbol values")
        self.button_encode.clicked.connect(self.encode)

        widget_encode_layout.addWidget(self.button_encode)
        widget_encode_layout.addWidget(self.button_encode_and_transmit)
        self.widget_encode.setLayout(widget_encode_layout)

        self.label_symbol_values = QLabel("Symbol values")
        self.label_symbol_values.setObjectName('subheader')
        self.text_edit_symbol_values = QTextEdit()

        self.widget_transmission = QWidget()
        widget_transmission_layout = QHBoxLayout()

        self.button_transmit_symbol_values = QPushButton("Transmit")
        self.button_transmit_symbol_values.setIcon(ViewUtils.get_icon('send'))
        self.button_transmit_symbol_values.setToolTip('Transmit symbol values')
        self.button_transmit_symbol_values.clicked.connect(self.transmit_symbol_values)
        self.button_cancel_transmission = QPushButton("Cancel")
        self.button_cancel_transmission.setIcon(ViewUtils.get_icon('cancel'))
        self.button_cancel_transmission.setToolTip('Cancel transmission')
        self.button_cancel_transmission.clicked.connect(self.cancel_transmission)

        widget_transmission_layout.addWidget(self.button_transmit_symbol_values)
        widget_transmission_layout.addWidget(self.button_cancel_transmission)
        self.widget_transmission.setLayout(widget_transmission_layout)

        self.progress_bar_transmission = QProgressBar()
        self.progress_bar_transmission.setValue(0)

        if self.has_parameters:
            self.layout.addWidget(self.widget_label_parameters)
            self.layout.addWidget(self.table_parameters)

        self.layout.addWidget(self.widget_sequence)
        self.layout.addWidget(self.text_edit_sequence)
        self.layout.addWidget(self.widget_encode)

        self.layout.addWidget(self.label_symbol_values)
        self.layout.addWidget(self.text_edit_symbol_values)
        self.layout.addWidget(self.widget_transmission)
        self.layout.addWidget(self.progress_bar_transmission)

        self.button_add_encoder.setEnabled(False)
        self.button_remove_encoder.setEnabled(True)

    def encoder_removed(self):
        """
        Do stuff when the encoder is removed.
        """
        self.widget_sequence.deleteLater()
        self.text_edit_sequence.deleteLater()
        self.widget_encode.deleteLater()
        self.label_symbol_values.deleteLater()
        self.text_edit_symbol_values.deleteLater()
        self.widget_transmission.deleteLater()
        self.progress_bar_transmission.deleteLater()

        if self.has_parameters:
            self.widget_label_parameters.deleteLater()
            self.table_parameters.deleteLater()

        self.button_add_encoder.setEnabled(True)
        self.button_remove_encoder.setEnabled(False)

    def encode(self):
        """
        Encodes the sequence from the sequence text edit and puts it in the symbol values text edit.
        """
        sequence = self.text_edit_sequence.toPlainText()
        symbol_values_str = str(self.view.controller.encode_with_check(sequence))
        symbol_values_str = symbol_values_str.replace("[", "").replace("]", "").replace("'", "")
        self.text_edit_symbol_values.setText(symbol_values_str)

    def encode_and_transmit(self):
        """
        Encodes a sequence and directly transmits it.
        """
        self.encode()
        self.transmit_symbol_values()

    def load_sequence(self):
        """
        Loads a sequence from a file and puts it in the sequence text edit.
        """
        filename, _ = QFileDialog.getOpenFileName(self, 'Open File', './Sequences/', 'Text Files (*.txt)')
        if not filename == "":
            with open(filename, 'r') as file:
                sequence = file.read()
                self.text_edit_sequence.setText(sequence)

    def parameters_edited(self, parameter_values):
        """
        Update table when parameters are edited.
        :param parameter_values: New parameter values.
        """
        for i in range(len(parameter_values)):
            value = list(parameter_values.values())[i]
            self.table_parameters.setItem(i, 1, QTableWidgetItem(str(value)))

    def remove_encoder(self):
        """
        Removes the encoder.
        """
        if ViewUtils.message_box_warning(self.style(), "Remove encoder?", "Are you sure you want to remove the decoder?"):
            self.view.controller.remove_encoder()

    def transmit_symbol_values(self):
        """
        Transmits symbol values stored in the symbol values text edit.
        """
        symbol_values = self.text_edit_symbol_values.toPlainText().split(',')
        self.view.controller.transmit_symbol_values(symbol_values)

    def update_(self, encoder_info):
        """
        Updates the encoder view based of information from the encoder.
        :param encoder_info: Information about encoder.
        """
        transmitting = encoder_info['transmitting']
        transmission_progress = encoder_info['transmission_progress']
        self.button_encode_and_transmit.setEnabled(not transmitting)
        self.button_transmit_symbol_values.setEnabled(not transmitting)
        self.button_cancel_transmission.setEnabled(transmitting)
        self.progress_bar_transmission.setValue(transmission_progress)