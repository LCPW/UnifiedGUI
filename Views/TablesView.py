from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *


from Views import TableView

# TODO: Docu


class TablesView(QWidget):
    """
    Visualizes decoder data in the form of tables.
    """
    def __init__(self):
        """
        Initializes the table view widget.
        """
        super().__init__()

        layout = QVBoxLayout()

        self.tabs = QTabWidget()
        self.tables = []

        layout.addWidget(self.tabs)

        self.setLayout(layout)

    def decoder_added(self, decoder_info):
        """
        Do stuff when a decoder is added.
        :param decoder_info: Information about the decoder.
        """
        receiver_info = decoder_info['receivers']
        for receiver_index in range(receiver_info['num']):
            name, sensor_names = receiver_info['names'][receiver_index], receiver_info['sensor_names'][receiver_index]
            table = TableView.TableView(sensor_names)
            self.tables.append(table)
            self.tabs.addTab(self.tables[receiver_index], str(name))

    def decoder_removed(self):
        for table in self.tables:
            self.tabs.removeTab(self.tabs.indexOf(table))
        self.tables = []

    def update_(self, decoded):
        """
        Updates this widget with new information from the decoder.
        :param decoded: Decoder value updates.
        """
        received = decoded['received']
        self.update_values(received)

    def update_values(self, received):
        lengths, timestamps, values = received['lengths'], received['timestamps'], received['values']
        for i in range(len(timestamps)):
            if timestamps[i] is not None:
                self.tables[i].update_table(lengths[i], timestamps[i], values[i])