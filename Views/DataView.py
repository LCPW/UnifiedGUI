from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from Views import PlotView, TablesView


class DataView(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()

        self.tabs = QTabWidget()
        self.tab_tables = TablesView.TablesView()
        self.tab_plot = PlotView.PlotView()

        self.tabs.addTab(self.tab_tables, "Tables")
        self.tabs.addTab(self.tab_plot, "Plot")

        layout.addWidget(self.tabs)

        self.setLayout(layout)

    def add_receivers(self, count):
        self.tab_tables.add_tables(count)

    def update_values(self, vals):
        self.tab_tables.update_values(vals)
        self.tab_plot.update_values(vals)