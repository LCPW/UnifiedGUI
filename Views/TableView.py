from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from datetime import datetime


class TableView(QTableWidget):
    def __init__(self, column_names):
        super().__init__()

        self.old_length = 0
        self.num_columns = len(column_names) + 1

        # Row count
        self.setRowCount(0)

        # Column count
        self.setColumnCount(self.num_columns)

        self.setHorizontalHeaderLabels(["Timestamp"] + column_names)

        # Table will fit the screen horizontally
        self.horizontalHeader().setStretchLastSection(True)
        self.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

    def update_values(self, vals):
        len_vals = len(vals)
        self.setRowCount(len_vals)
        for i in range(self.old_length, len_vals):
            timestamp, values = vals[i]['timestamp'], vals[i]['values']
            self.setItem(i, 0, QTableWidgetItem(str(datetime.fromtimestamp(timestamp))))
            for j in range(0, len(values)):
                self.setItem(i, j+1, QTableWidgetItem(str(values[j])))
        self.old_length = len_vals