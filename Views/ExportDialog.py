from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *


class ExportDialog(QDialog):

    def __init__(self, controller):
        super(ExportDialog, self).__init__()

        self.setWindowTitle("Export data")
        self.setWindowIcon(QIcon('./Views/Icons/tune.png'))

        layout = QFormLayout()

        label_name = QLabel("Dataset name: ")
        self.line_name = QLineEdit()
        self.line_name.setMaxLength(120)
        self.line_name.setText("frequency_measurement")
        layout.addRow(label_name, self.line_name)

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

        label_encoder = QLabel("Save encoder activation")
        self.box_encoder = QCheckBox()
        self.box_encoder.setChecked(False)
        layout.addRow(label_encoder, self.box_encoder)

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
