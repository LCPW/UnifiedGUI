from PyQt5 import QtWidgets, QtCore, QtGui, Qt
import sys
import threading
import time

from Models import Model
from Views import View


FRAMES_PER_SECOND = 100


class Controller:
    def __init__(self):
        self.model = Model.Model()
        self.view = None

        self.running = True

        thread_gui = threading.Thread(target=self.run_gui, daemon=True)
        thread_gui.start()

        while self.view is None:
            time.sleep(0.1)

        # Main program loop
        while self.running:
            self.run(sleep_time=1.0/FRAMES_PER_SECOND)

        # TODO: Clean exit
        #self.view.timer.stop()
        #sys.exit(0)

    def run(self, sleep_time):
        # TODO: Do we even need to do something here?
        if self.model.is_decoder_available():
            self.model.decoder.decode()
        # This is necessary in order for the GUI not to freeze and crash at some point
        time.sleep(sleep_time)

    def run_gui(self):
        app = QtWidgets.QApplication(sys.argv)
        app.setStyle('Fusion')
        # Disables the question mark in dialog windows
        app.setAttribute(QtCore.Qt.AA_DisableWindowContextHelpButton)
        self.view = View.View(self)
        self.view.show()
        app.exec_()
        #sys.exit(app.exec_())

    def get_decoded(self):
        return self.model.get_decoded()

    def add_encoder(self, encoder_type):
        self.model.add_encoder(encoder_type)

    def remove_encoder(self):
        self.model.remove_encoder()

    def add_decoder(self, decoder_type):
        # TODO: Test
        parameters = self.model.get_decoder_parameters(decoder_type)
        # No parameters defined -> No parameter values obviously
        if parameters is None:
            parameter_values = None
        # Parameters defined -> Execute ParameterDialog
        else:
            # User clicked Ok Button -> Everything is fine, get the values and continue
            if self.view.get_parameter_values(parameters):
                parameter_values = self.view.parameter_dialog.values
            # User clicked Cancel -> Do not add decoder
            else:
                return

        self.model.add_decoder(decoder_type, parameter_values)
        receiver_info = self.model.get_receiver_info()
        landmark_info = self.model.get_landmark_info()
        self.view.decoder_added(decoder_type, receiver_info, landmark_info)

    def remove_decoder(self):
        self.model.remove_decoder()
        self.view.decoder_removed()

    def start_decoder(self):
        self.model.start_decoder()
        self.view.decoder_view.decoder_started()

    def stop_decoder(self):
        self.model.stop_decoder()
        self.view.decoder_view.decoder_stopped()

    def close(self):
        self.running = False