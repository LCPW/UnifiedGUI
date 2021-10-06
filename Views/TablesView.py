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

    def add_tables(self, receiver_info):
        for i in range(len(receiver_info)):
            description, sensor_descriptions = receiver_info[i]
            table = TableView.TableView(sensor_descriptions)
            self.tables.append(table)
            self.tabs.addTab(self.tables[i], str(description))

    def remove_tables(self):
        for table in self.tables:
            self.tabs.removeTab(self.tabs.indexOf(table))
        self.tables = []

    def update_values(self, vals):
        for i in range(len(vals)):
            self.tables[i].update_values(vals[i])