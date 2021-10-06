from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *


class TableView(QTableWidget):
    def __init__(self, column_names):
        super().__init__()

        self.old_length = 0
        self.num_columns = len(column_names)

        # Row count
        self.setRowCount(0)

        # Column count
        self.setColumnCount(self.num_columns)

        self.setHorizontalHeaderLabels(column_names)

        # Table will fit the screen horizontally
        self.horizontalHeader().setStretchLastSection(True)
        self.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

    def update_values(self, vals):
        len_vals = len(vals)
        self.setRowCount(len_vals)
        for i in range(self.old_length, len_vals):
            for j in range(self.num_columns):
                self.setItem(i, j, QTableWidgetItem(str(vals[i][j])))
        self.old_length = len_vals