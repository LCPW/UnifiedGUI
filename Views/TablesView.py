from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *


from Views import TableView


class TablesView(QWidget):
    def __init__(self):
        super().__init__()

        layout = QVBoxLayout()

        self.tabs = QTabWidget()
        self.tables = []

        layout.addWidget(self.tabs)

        self.setLayout(layout)

    def decoder_added(self, receiver_info):
        for i in range(len(receiver_info)):
            description, sensor_descriptions = receiver_info[i]['description'], receiver_info[i]['sensor_descriptions']
            table = TableView.TableView(sensor_descriptions)
            self.tables.append(table)
            self.tabs.addTab(self.tables[i], str(description))

    def decoder_removed(self):
        for table in self.tables:
            self.tabs.removeTab(self.tabs.indexOf(table))
        self.tables = []

    def update_tables(self, vals):
        timestamps, values = vals['timestamps'], vals['values']
        for i in range(len(timestamps)):
            if timestamps[i] is not None:
                self.tables[i].update_table(timestamps[i], values[i])