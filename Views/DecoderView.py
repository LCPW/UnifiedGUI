from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from Utils import ViewUtils


# class DecoderDockWidget(QDockWidget):
#     def __init__(self, main_view):
#         super().__init__()
#         decoder_view = DecoderView(main_view)
#         self.setWidget(decoder_view)


class DecoderView(QWidget):
    """
    The decoder view shows information about the decoder and the receivers and provides the option to
    add/remove/start/stop a decoder as well as to edit the decoder parameters.
    """
    def __init__(self, view):
        """
        Initializes the decoder view widget.
        :param view: Main window.
        """
        super().__init__()

        self.view = view

        self.layout = QVBoxLayout()

        self.toolbar = QToolBar()

        self.button_add_decoder = QToolButton()
        self.button_add_decoder.setToolTip("Add Decoder")
        self.button_add_decoder.setIcon(ViewUtils.get_icon('add'))
        self.button_add_decoder.clicked.connect(self.add_decoder)
        self.toolbar.addWidget(self.button_add_decoder)

        self.button_remove_decoder = QToolButton()
        self.button_remove_decoder.setToolTip("Remove Decoder")
        self.button_remove_decoder.setIcon(ViewUtils.get_icon('remove'))
        self.button_remove_decoder.setEnabled(False)
        self.button_remove_decoder.clicked.connect(self.remove_decoder)
        self.toolbar.addWidget(self.button_remove_decoder)

        self.button_start_decoder = QToolButton()
        self.button_start_decoder.setToolTip("Start Decoder")
        self.button_start_decoder.setIcon(ViewUtils.get_icon('play'))
        self.button_start_decoder.setEnabled(False)
        self.button_start_decoder.clicked.connect(self.start_decoder)
        self.toolbar.addWidget(self.button_start_decoder)

        self.button_stop_decoder = QToolButton()
        self.button_stop_decoder.setToolTip("Stop Decoder")
        self.button_stop_decoder.setIcon(ViewUtils.get_icon('stop'))
        self.button_stop_decoder.setEnabled(False)
        self.button_stop_decoder.clicked.connect(self.stop_decoder)
        self.toolbar.addWidget(self.button_stop_decoder)

        self.button_parameters = QToolButton()
        self.button_parameters.setToolTip("Edit Parameters")
        self.button_parameters.setIcon(ViewUtils.get_icon('tune'))
        self.button_parameters.setEnabled(False)
        self.button_parameters.clicked.connect(self.view.controller.edit_decoder_parameters)
        self.toolbar.addWidget(self.button_parameters)

        label = QLabel("Decoder")
        label.setObjectName("header")

        self.label_subtitle = QLabel("No decoder selected")

        self.layout.addWidget(label)
        self.layout.addWidget(self.label_subtitle)
        self.layout.addWidget(ViewUtils.line_h())
        self.layout.addWidget(self.toolbar)
        self.layout.addWidget(ViewUtils.line_h())
        self.layout.addStretch(1)

        self.setLayout(self.layout)

        self.label_symbol_values = None
        self.text_edit_symbol_values = None
        self.label_sequence = None
        self.text_edit_sequence = None
        self.label_parameters = None
        self.table_parameters = None

    def add_decoder(self):
        """
        Add a new decoder.
        """
        names = self.view.controller.get_available_decoders()

        decoder_type, ok = QInputDialog.getItem(self, "Add Decoder", "Decoder type", names, 0, False)
        if ok:
            self.view.controller.add_decoder(decoder_type)

    def decoder_added(self, decoder_info):
        """
        Do stuff when a decoder is added.
        :param decoder_info: Information about the newly added decoder.
        """
        parameter_values = decoder_info['parameter_values']
        self.label_subtitle.setText(decoder_info['type'])

        if parameter_values:
            self.label_parameters = QLabel("Parameter values")
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
            #self.table_parameters.resizeRowsToContents()
            for i in range(len(parameter_values)):
                description = list(parameter_values.keys())[i]
                value = parameter_values[description]
                self.table_parameters.setItem(i, 0, QTableWidgetItem(str(description)))
                self.table_parameters.setItem(i, 1, QTableWidgetItem(str(value)))
            self.button_parameters.setEnabled(True)

        self.label_sequence = QLabel("Sequence")
        self.text_edit_sequence = QPlainTextEdit()
        self.text_edit_sequence.setReadOnly(True)

        self.label_symbol_values = QLabel("Symbol values")
        self.text_edit_symbol_values = QPlainTextEdit()
        self.text_edit_symbol_values.setReadOnly(True)

        if parameter_values:
            self.layout.addWidget(self.label_parameters)
            self.layout.addWidget(self.table_parameters)

        self.layout.addWidget(self.label_sequence)
        self.layout.addWidget(self.text_edit_sequence)

        self.layout.addWidget(self.label_symbol_values)
        self.layout.addWidget(self.text_edit_symbol_values)

        self.button_add_decoder.setEnabled(False)
        self.button_remove_decoder.setEnabled(True)
        self.button_start_decoder.setEnabled(True)
        self.button_stop_decoder.setEnabled(False)

    def decoder_removed(self):
        """
        Do stuff when the decoder is removed.
        """
        self.label_subtitle.setText("No decoder selected.")

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
        """
        Do stuff when the decoder is started.
        """
        self.button_add_decoder.setEnabled(False)
        self.button_remove_decoder.setEnabled(False)
        self.button_start_decoder.setEnabled(False)
        self.button_stop_decoder.setEnabled(True)

    def decoder_stopped(self):
        """
        Do stuff when the decoder is stopped.
        """
        self.button_add_decoder.setEnabled(False)
        self.button_remove_decoder.setEnabled(True)
        self.button_start_decoder.setEnabled(False)
        self.button_stop_decoder.setEnabled(False)

    def parameters_edited(self, parameter_values):
        """
        Update table when parameters are edited.
        :param parameter_values: New parameter values.
        """
        for i in range(len(parameter_values)):
            value = list(parameter_values.values())[i]
            self.table_parameters.setItem(i, 1, QTableWidgetItem(str(value)))

    def remove_decoder(self):
        """
        Removes the decoder.
        """
        if ViewUtils.message_box_warning(self.style(), "Remove decoder?", "Are you sure you want to remove the decoder?", "All data that has not been exported yet, cannot be recovered."):
            self.view.controller.remove_decoder()

    def start_decoder(self):
        """
        Starts the decoder.
        """
        self.view.controller.start_decoder()

    def stop_decoder(self):
        """
        Stops the decoder.
        """
        if ViewUtils.message_box_warning(self.style(), "Stop decoder?", "Are you sure you want to stop the decoder?", "Once the decoder is stopped, no more new data can be shown."):
            self.view.controller.stop_decoder()

    def update_(self, decoded):
        """
        Updates the decoder view based on new information from the decoder.
        :param decoded: New decoder information.
        """
        symbol_values, sequence = decoded['symbol_values'], decoded['sequence']
        self.update_symbol_values(symbol_values)
        self.update_sequence(sequence)

    def update_sequence(self, sequence):
        """
        Updates the displayed sequence.
        :param sequence: New sequence from the decoder.
        """
        self.text_edit_sequence.setPlainText(sequence)

    def update_symbol_values(self, symbol_values):
        """
        Converts symbol values list to a string and updates the displayed symbol values.
        :param symbol_values: New symbol values from the decoder.
        """
        symbol_values_str = str(symbol_values)
        symbol_values_str = symbol_values_str.replace("[", "").replace("]", "").replace("'", "")
        self.text_edit_symbol_values.setPlainText(symbol_values_str)