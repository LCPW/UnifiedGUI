from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from Views import PlotView, TablesView


class DataView(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()

        self.tabs = QTabWidget()
        self.tab_table = TablesView.TablesView()
        self.tab_plot = PlotView.PlotView()

        self.tabs.addTab(self.tab_table, "Tables")
        self.tabs.addTab(self.tab_plot, "Plot")

        layout.addWidget(self.tabs)

        self.setLayout(layout)

    def update_values(self, vals):
        self.tab_table.update_values(vals)
        self.tab_plot.update_values(vals)