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

    def decoder_clear(self):
        """
        Clears elements from the plot and tables.
        """
        self.tab_plot.decoder_clear()
        self.tab_tables.decoder_clear()

    def decoder_removed(self):
        """
        Do stuff when the decoder is removed.
        """
        self.tab_tables.decoder_removed()
        self.tab_plot.decoder_removed()

    def encoder_added(self, encoder_info):
        """
        Do stuff when a encoder is added.
        :param encoder_info: Information about encoder.
        """
        # self.tab_tables.encoder_added(encoder_info)
        self.tab_plot.encoder_added(encoder_info)

    def encoder_clear(self):
        """
        Clears elements from the plot and tables.
        """
        self.tab_plot.encoder_clear()
        # self.tab_tables.encoder_clear()

    def encoder_removed(self):
        """
        Do stuff when the encoder is removed.
        """
        # self.tab_tables.encoder_removed()
        self.tab_plot.encoder_removed()

    def update_(self, decoded, encoded):
        """
        Updates this widget with new information from the decoder.
        :param decoded: Decoder value updates.
        :param encoded: Encoder value updates.
        """
        self.tab_plot.update_(decoded, encoded=encoded)
        if decoded is not None:
            self.tab_tables.update_(decoded)
