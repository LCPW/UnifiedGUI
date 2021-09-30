from PyQt5 import QtWidgets, QtCore, QtGui, Qt
import sys
import threading
import time

from Models import Model
from Views import MainView


FRAMES_PER_SECOND = 25


class Controller:
    def __init__(self):
        self.model = Model.Model()
        self.view = None

        self.running = True

        thread_gui = threading.Thread(target=self.run_gui)
        thread_gui.start()

        while self.view is None:
            time.sleep(0.1)

        # Main program loop
        while self.running:
            self.run(sleep_time=1.0/FRAMES_PER_SECOND)

    def run(self, sleep_time):
        decoded = self.model.get_decoded()
        received = self.model.get_received()
        self.view.update_values(received)
        # This is necessary in order for the GUI not to freeze and crash at some point
        time.sleep(sleep_time)

    def run_gui(self):
        app = QtWidgets.QApplication(sys.argv)
        app.setStyle('Fusion')
        self.view = MainView.MainView(self)
        self.view.show()
        sys.exit(app.exec_())

    def add_encoder(self, encoder_type):
        self.model.add_encoder(encoder_type)

    def remove_encoder(self):
        self.model.remove_encoder()

    def add_decoder(self, decoder_type):
        self.model.add_decoder(decoder_type)

    def remove_decoder(self):
        self.model.remove_decoder()

    def close(self):
        self.running = False