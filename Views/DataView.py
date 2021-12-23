from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from Views import PlotView, TablesView


class DataView(QWidget):
    """
    Widget responsible for visualizing the data from the decoder.
    Two representation are available: Live plot and tables.
    """
    def __init__(self, view):
        """
        Initializes the data view.
        :param view: Reference to main view widget.
        """
        super().__init__()
        layout = QVBoxLayout()

        self.view = view

        self.tabs = QTabWidget()
        self.tab_tables = TablesView.TablesView()
        self.tab_plot = PlotView.PlotView(self)

        self.tabs.addTab(self.tab_plot, "Plot")
        self.tabs.addTab(self.tab_tables, "Tables")

        layout.addWidget(self.tabs)

        self.setLayout(layout)

    def decoder_added(self, decoder_info):
        """
        Do stuff when a decoder is added.
        :param decoder_info: Information about decoder.
        """
        self.tab_tables.decoder_added(decoder_info)
        self.tab_plot.decoder_added(decoder_info)

    def decoder_removed(self):
        """
        Do stuff when the decoder is removed.
        """
        self.tab_tables.decoder_removed()
        self.tab_plot.decoder_removed()

    def update_(self, decoded):
        """
        Updates this widget with new information from the decoder.
        :param decoded: Decoder value updates.
        """
        self.tab_plot.update_(decoded)
        self.tab_tables.update_(decoded)