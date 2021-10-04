from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *


class TableView(QTableWidget):
    def __init__(self):
        super().__init__()

        headers = ["Timestamp", "Value"]

        # Row count
        self.setRowCount(0)

        # Column count
        self.setColumnCount(2)

        self.setHorizontalHeaderLabels(headers)

        # Table will fit the screen horizontally
        self.horizontalHeader().setStretchLastSection(True)
        self.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

    def update_values(self, vals):
        len_vals = len(vals)
        self.setRowCount(len_vals)
        for i in range(len_vals):
            t, x = vals[i]
            self.setItem(i, 0, QTableWidgetItem(str(t)))
            self.setItem(i, 1, QTableWidgetItem(str(x)))