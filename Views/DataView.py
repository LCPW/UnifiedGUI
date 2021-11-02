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

    def decoder_added(self, receiver_info, landmark_info):
        self.tab_tables.decoder_added(receiver_info)
        self.tab_plot.decoder_added(receiver_info, landmark_info)

    def decoder_removed(self):
        self.tab_tables.decoder_removed()
        self.tab_plot.decoder_removed()

    def update_values(self, vals):
        self.tab_tables.update_values(vals)
        self.tab_plot.update_values(vals)

    def update_landmarks(self, landmarks):
        self.tab_plot.update_landmarks(landmarks)

    def update_symbol_intervals(self, symbol_intervals):
        self.tab_plot.update_symbol_intervals(symbol_intervals)

    def update_symbol_values(self, symbol_intervals, symbol_values):
        self.tab_plot.update_symbol_values(symbol_intervals, symbol_values)