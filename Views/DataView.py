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

        self.tabs.addTab(self.tab_plot, "Plot")
        self.tabs.addTab(self.tab_tables, "Tables")

        layout.addWidget(self.tabs)

        self.setLayout(layout)

    def add_receivers(self, receiver_info):
        self.tab_tables.add_tables(receiver_info)
        self.tab_plot.add_datalines(receiver_info)

    def remove_receivers(self):
        self.tab_tables.remove_tables()
        self.tab_plot.remove_datalines()
        # TODO: Plot

    def update_values(self, vals):
        self.tab_tables.update_values(vals)
        self.tab_plot.update_values(vals)

    def update_symbol_intervals(self, symbol_intervals):
        self.tab_plot.update_symbol_intervals(symbol_intervals)

    def update_symbol_values(self, symbol_intervals, symbol_values):
        self.tab_plot.update_symbol_values(symbol_intervals, symbol_values)