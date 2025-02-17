from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *


class ExportDialog(QDialog):

    TIME_FORMAT_OPTIONS = ['System timestamps',  # current time in seconds since the Epoch
                           'Basic timestamps (t0 = 0)'  # time in seconds subtracted based on the first timestamp
                            ]

    def __init__(self, controller):
        super(ExportDialog, self).__init__()

        self.setWindowTitle("Export data")
        self.setWindowIcon(QIcon('./Views/Icons/tune.png'))

        layout = QFormLayout()

        label_name = QLabel("Dataset name: ")
        self.line_name = QLineEdit()
        self.line_name.setMaxLength(120)
        self.line_name.setText("frequency_measurement")
        label_test = QLabel(".xlsx")
        layout2 = QFormLayout()
        layout2.addRow(self.line_name, label_test)
        layout.addRow(label_name, layout2)

        label_encoder = QLabel("Save encoder activation")
        self.box_encoder = QCheckBox()
        self.box_encoder.setChecked(controller.model.is_encoder_present())
        layout.addRow(label_encoder, self.box_encoder)

        label_time_format = QLabel("Time format")
        self.box_time_format = QComboBox()
        self.box_time_format.addItems(self.TIME_FORMAT_OPTIONS)
        layout.addRow(label_time_format, self.box_time_format)

        label_additional = QLabel("Save additional datalines")
        self.box_additional = QCheckBox()
        self.box_additional.setChecked(False)
        layout.addRow(label_additional, self.box_additional)

        label_name_additional = QLabel("Additional dataset name: ")
        self.line_name_additional = QLineEdit()
        self.line_name_additional.setMaxLength(120)
        self.line_name_additional.setText("additional_measurement")
        self.line_name_additional.setEnabled(self.box_additional.isChecked())
        layout.addRow(label_name_additional, self.line_name_additional)
        self.box_additional.stateChanged.connect(self.box_additional_state_changed)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addRow(buttons)

        self.setLayout(layout)

    def box_additional_state_changed(self):
        self.line_name_additional.setEnabled(self.box_additional.isChecked())

    def has_selected_additional_datalines(self):
        return self.box_additional.isChecked()

    def get_data_name(self):
        return self.line_name.text()

    def get_additional_data_name(self):
        if self.has_selected_additional_datalines():
            return self.line_name_additional.text()
        else:
            return None

    def has_selected_encoder_activation(self):
        return self.box_encoder.isChecked()

    def has_selected_system_timestamps(self):
        return self.box_time_format.currentIndex() == 0
