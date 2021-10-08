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

    def update(self):
        self.tab_plot.update()

    def add_receivers(self, receiver_info):
        self.tab_tables.add_tables(receiver_info)
        self.tab_plot.add_datalines(receiver_info)

    def remove_receivers(self):
        self.tab_tables.remove_tables()
        # TODO: Plot

    def update_values(self, vals):
        self.tab_tables.update_values(vals)
        self.tab_plot.update_values(vals)