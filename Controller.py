from PyQt5 import QtWidgets, QtCore, QtGui, Qt
import sys
import threading
import time
import logging
import os
import xlsxwriter
from xlsxwriter.exceptions import FileCreateError

from Models import Model
from Views import View
from Utils.Settings import SettingsStore
from Utils import Logging, ViewUtils

import version


class Controller:
    """
    The controller is responsible for executing the main program logic.
    It has references to the model and the view. Every communication between these two is handeled by the controller.
    """
    def __init__(self):
        """
        Initialize controller.
        """
        self.model = Model.Model()
        self.view = None

        self.running = True

        self.lock_view = threading.Lock()
        self.thread_gui = threading.Thread(target=self.run_gui, daemon=True)
        self.thread_gui.start()

    def start(self):
        with self.lock_view:  # will only start, when self.view has been initialized
            Logging.info("Starting UnifiedGUI [Version %s]." % (version.__version__))

        # Main program loop
        fps = SettingsStore.settings['FRAMES_PER_SECOND']
        while self.running:
            self.run(sleep_time=1.0 / fps)

        self.shutdown()

    def add_decoder(self, decoder_type=None, decoder=None):
        """
        Adds a new decoder.
        :param decoder_type: Decoder type.
        :param decoder: decoder object (default: None)
        """

        if decoder_type is not None:
            parameters = self.model.get_decoder_parameters(decoder_type)
            # No parameters defined -> No parameter values obviously
            if parameters is None:
                parameter_values = None
            # Parameters defined -> Execute ParameterDialog
            else:
                ok, values = ViewUtils.get_parameter_values(parameters)
                # User clicked Ok Button -> Everything is fine, get the values and continue
                if ok:
                    parameter_values = values
                # User clicked Cancel -> Do not add decoder
                else:
                    return

            try:
                decoder_info = self.model.add_decoder(decoder_type, parameters, parameter_values)
                decoder_info.update({'parameter_values': parameter_values})
                self.view.decoder_added(decoder_info)
            except Exception as e:
                Logging.error(e.args[0])
                Logging.error("Failed to add decoder. Make sure device is connected and not used by other applications.")

        elif decoder is not None:
            decoder_info = self.model.add_decoder_object(decoder)
            decoder_info.update({'parameter_values': decoder.parameter_values})
            self.view.decoder_added(decoder_info)

    def add_encoder(self, encoder_type):
        """
        Adds a new encoder
        :param encoder_type: Encoder type.
        """
        parameters = self.model.get_encoder_parameters(encoder_type)
        # No parameters defined -> No parameter values obviously
        if parameters is None:
            parameter_values = None
        # Parameters defined -> Execute ParameterDialog
        else:
            ok, values = ViewUtils.get_parameter_values(parameters)
            # User clicked Ok Button -> Everything is fine, get the values and continue
            if ok:
                parameter_values = values
            # User clicked Cancel -> Do not add decoder
            else:
                return

        try:
            encoder_info = self.model.add_encoder(encoder_type, parameters, parameter_values)
            encoder_info.update({'parameter_values': parameter_values})
            self.view.encoder_added(encoder_info)
        except Exception as e:
            Logging.error(e.args[0])
            Logging.error("Failed to add encoder. Make sure device is connected and not used by other applications.")

    def cancel_transmission(self):
        """
        Cancels an ongoing transmission.
        This is executed when the user clicks on the Cancel button.
        """
        self.model.encoder.cancel_transmission()

    def close(self):
        """
        Closes UnifiedGUI.
        This is executed when the user confirms the exit dialog.
        """
        self.running = False

    def clear_decoder(self):
        """
        Clears decoder.
        This is called when the user presses on the Clear button.
        """
        self.view.decoder_clear()
        self.model.decoder.clear()

    def clear_encoder_recording(self):
        """
        Clears encoder recording.
        This is called when the user presses on the Start button.
        """
        self.model.encoder.clear_recording()

    def edit_decoder_parameters(self):
        """
        Let the user edit the decoder parameters by executing a dialog.
        """
        parameters = self.model.decoder.parameters
        current_values = list(self.model.decoder.parameter_values.values())

        ok, parameter_values = ViewUtils.get_parameter_values(parameters, current_values)
        # User clicked Ok Button -> Everything is fine, get the values and continue
        if ok:
            decoder = self.model.decoder
            self.remove_decoder()
            decoder.parameters_edited(parameter_values)
            self.add_decoder(decoder=decoder)
            # self.view.decoder_view.parameters_edited(parameter_values)

    def edit_encoder_parameters(self):
        """
        Let the user edit the encoder parameters by executing a dialog.
        """
        parameters = self.model.encoder.parameters
        current_values = list(self.model.encoder.parameter_values.values())

        ok, parameter_values = ViewUtils.get_parameter_values(parameters, current_values)
        # User clicked Ok Button -> Everything is fine, get the values and continue
        if ok:
            self.model.encoder.parameter_values = parameter_values
            self.model.encoder.parameters_edited()
            self.view.encoder_view.parameters_edited(parameter_values)

    def encode_with_check(self, sequence):
        return self.model.encoder.encode_with_check(sequence)

    def export_custom(self, directory, dataset_name, time_format_system, save_encoder_activation, dataset_additional_name):
        """
        ...
        :param directory: Directory for the data files to be stored.
        :param dataset_name: File name prefix of the main dataset file.
        :param time_format_system: True if the system time (seconds since epoch) should be used, otherwise false.
        :param save_encoder_activation: True or False, whether the encoder activation will be saved as part of the data
        :param dataset_additional_name: File name prefix for additional data .csv files. If not wanted, set to None
        """
        export_possible = self.model.decoder is not None or (save_encoder_activation and self.model.encoder is not None)

        if export_possible:
            # Create a new workbook for the datasets
            filename = os.path.join(directory, dataset_name + ".xlsx")
            workbook = xlsxwriter.Workbook(filename)

            if self.model.decoder is not None:
                self.model.decoder.export_custom(workbook, directory, time_format_system, dataset_additional_name)

            if save_encoder_activation and self.model.encoder is not None:
                self.model.encoder.export_custom(workbook, time_format_system)

            # Save the metadata of the current software
            worksheet_metadata = workbook.add_worksheet('Metadata')
            worksheet_metadata.write(0, 0, 'Software-Version')
            worksheet_metadata.write(0, 1, version.__version__)

            # Save the dataset
            try:
                workbook.close()
            except FileCreateError as e:
                Logging.error("Could not save the dataset, the file could not be written!", repeat=True)
        else:
            Logging.error('No decoder selected. Export of data is not possible!')

    def export_sequence(self, filename):
        self.model.decoder.export_sequence(filename)

    def export_symbol_values(self, filename):
        self.model.decoder.export_symbol_values(filename)

    def get_available_decoders(self):
        """
        Get a list of available decoders.
        :return: List of available decoders.
        """
        return self.model.get_available_decoders()

    def get_available_encoders(self):
        """
        Get a list of available encoders.
        :return: List of available encoders.
        """
        return self.model.get_available_encoders()

    def get_decoded(self):
        """
        Gets value updates from the decoder.
        Note: Do not use is_decoder_available, since get_decoded also gets executed when the plot is not active (stopped).
        :return: Decoder value updates if they are available, else None.
        """
        return self.model.get_decoded()

    def get_decoder_info(self):
        """
        Gets information about decoder.
        Decoder type, receiver information, landmark information.
        :return: Decoder information dictionary if decoder exists, else None.
        """
        return self.model.get_decoder_info()

    def get_encoded(self):
        """
        Gets value updates from the encoder.
        :return: Encoder value updates if they are available, else None.
        """
        return self.model.get_encoded()

    def get_encoder_info(self):
        """
        Gets information about encoder.
        :return: Encoder information dictionary if decoder exists, else None.
        """
        return self.model.get_encoder_info()

    def remove_decoder(self):
        """
        Removes the decoder.
        """
        self.model.remove_decoder()
        self.view.decoder_removed()

    def remove_encoder(self):
        """
        Removes the encoder.
        """
        self.model.remove_encoder()
        self.view.encoder_removed()

    def run(self, sleep_time):
        """
        Main progam loop.
        :param sleep_time: Sleep time in seconds, this is necessary in order for the GUI not to freeze and crash at some point.
        """
        if self.model.is_decoder_active():
            self.model.decoder.decode()

        if self.model.is_encoder_recording():
            self.model.encoder.update_datalines()
        time.sleep(sleep_time)

    def run_gui(self):
        """
        Runs the graphical user interface (GUI).
        This method will be executed in a new thread in __init__.
        Note: From a logical point of view, it would make more sense for this to be inside /Views/View.py.
              However, I could not find a way to make it work this way due to some issues I did not fully understand.
              This seems to be the most understandable solution to avoid these issues.
        """
        with self.lock_view:
            app = QtWidgets.QApplication(sys.argv)
            app.setStyle('Fusion')
            # Use stylesheet
            with open('./Views/Style.qss', 'r') as f:
                app.setStyleSheet(f.read())
            # Disables the question mark in dialog windows
            app.setAttribute(QtCore.Qt.AA_DisableWindowContextHelpButton)
            self.view = View.View(self)
            self.view.show()
        app.exec_()

    def shutdown(self):
        """
        Performs some cleanup before actually stopping UnifiedGUI.
        """

        try:
            self.cancel_transmission()
            self.model.encoder.shutdown()
        except:
            pass

        try:
            self.stop_decoder()
            self.model.decoder.shutdown()
        except:
            pass

        self.view.timer.stop()
        # Save settings
        try:
            self.view.data_view.tab_plot.settings_object.save()
        # No settings object
        except AttributeError:
            pass
        SettingsStore.shutdown()
        # Do not show any exception when something fails while shutting down
        logging.raiseExceptions = False
        logging.shutdown()

        #self.view.close_all_windows()

        # os._exit() needed instead of sys.exit() to kill all threads
        os._exit(0)

    def start_decoder(self):
        """
        Starts the decoder.
        """
        self.clear_decoder()
        try:
            self.model.start_decoder()
            self.view.decoder_started()
        except Exception as e:
            Logging.error(e.args[0])
            Logging.error("Failed to start decoder.")

    def start_encoder_recording(self):
        """
        Starts the encoder recording.
        """
        self.clear_encoder_recording()

        self.model.encoder.set_recording(True)
        self.view.encoder_started_recording()

    def stop_decoder(self):
        """
        Stops the decoder.
        """
        try:
            self.model.stop_decoder()
            self.view.decoder_view.decoder_stopped()
        except Exception as e:
            Logging.error(e.args[0])
            Logging.error("Failed to stop decoder.")

    def stop_encoder_recording(self):
        """
        Stops the encoder recording.
        """
        self.model.encoder.set_recording(False)

    def transmit_symbol_values(self, symbol_values):
        """
        Transmit given symbol values.
        :param symbol_values: Symbol values to transmit.
        """
        trimmed_values = [val.strip() for val in symbol_values]
        self.model.encoder.transmit_symbol_values(trimmed_values)