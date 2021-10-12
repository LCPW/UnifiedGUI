from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *


class PlotSettingsDialog(QDialog):
    def __init__(self, plot_view):
        super().__init__()

        self.plot_view = plot_view

        self.setWindowTitle("Plot Settings")
        self.setModal(False)

        self.layout = QVBoxLayout()

        self.checkbox_widget = QWidget()
        self.checkbox_layout = QHBoxLayout()
        self.checkbox_widget.setLayout(self.checkbox_layout)
        self.layout.addWidget(self.checkbox_widget)

        self.setLayout(self.layout)

    def add_receivers(self, receiver_info):
        for i in range(len(receiver_info)):
            description, sensor_descriptions = receiver_info[i]['description'], receiver_info[i]['sensor_descriptions']
            widget = QWidget()
            layout = QVBoxLayout()
            checkbox = QCheckBox(description)
            checkbox.setTristate(True)
            checkbox.setChecked(True)
            layout.addWidget(checkbox)

            for j in range(len(sensor_descriptions)):
                checkbox = QCheckBox(sensor_descriptions[j])
                checkbox.setChecked(True)
                layout.addWidget(checkbox)

            widget.setLayout(layout)
            self.checkbox_layout.addWidget(widget)

    def checkbox(self, receiver_index, sensor_index):
        # TODO
        # Toggle selected checkbox
        # Check if the tri-state checkbox needs to be updated
        # Update settings dict
        pass
