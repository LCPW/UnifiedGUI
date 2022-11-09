import importlib
import threading
import numpy as np
import time
import os
import csv

from Utils import Logging
from Utils.Settings import SettingsStore


class DecoderInterface:
    """
    A decoder consists of m receivers. In the simplest case, the decoder just
    collects data from the receivers and stores them. A decoder may also
    provide more functionality, as it allows for further processing to retrieve
    information from the data generated by the receivers.
    """
    def __init__(self, parameters, parameter_values):
        """
        Initializes the decoder.
        :param parameters: Information about parameters.
        :param parameter_values: User-defined parameter values.
        """
        self.parameters = parameters
        self.parameter_values = parameter_values

        self.active = False
        self.additional_datalines = []
        self.additional_datalines_names = None
        self.decoded = None
        self.info = None
        self.landmarks = []
        self.landmark_names = None
        self.landmark_symbols = None
        self.lengths = []
        self.min_timestamp = time.time()
        self.max_timestamp = time.time()
        self.num_additional_datalines = 0
        self.num_landmarks = 0
        self.num_receivers = 0
        self.plot_settings = {}
        self.received = []
        self.receivers = []
        self.receiver_names = None
        self.sequence = ""
        self.symbol_intervals = []
        self.symbol_values = []
        self.timestamps = []

    def setup(self):
        """
        Performs some further initialization.
        This method is called at the end of the initialization of the conrete decoder implementation.
        """
        self.num_receivers = len(self.receivers)

        if self.receiver_names is None:
            Logging.info("No receiver names provided, automatically generating them.")
            self.receiver_names = [str(self.receivers[i].__class__.__name__) + str(i + 1) for i in range(self.num_receivers)]

        if self.landmark_names is None:
            self.landmark_names = []
        else:
            self.num_landmarks = len(self.landmark_names)

        if self.additional_datalines_names is None:
            self.additional_datalines_names = []
        else:
            self.num_additional_datalines = len(self.additional_datalines_names)

        self.info = {
            'type': self.__class__.__name__,
            'landmarks': {
                'num': self.num_landmarks,
                'names': self.landmark_names,
            },
            'additional_datalines': {
                'num': self.num_additional_datalines,
                'names': self.additional_datalines_names
            },
            'plot_settings': self.plot_settings,
            'receivers': {
                'num': self.num_receivers,
                'names': self.receiver_names,
                'sensor_names': []
            }
        }

        for receiver_index in range(self.num_receivers):
            self.timestamps.append(None)
            self.received.append(None)
            self.lengths.append(0)
            self.info['receivers']['sensor_names'].append(self.receivers[receiver_index].sensor_names)

        self.additional_datalines = [None] * self.num_additional_datalines
        self.landmarks = [None] * self.num_landmarks

    def append(self, receiver_index, timestamp, values):
        """
        Appends a new timestamp for a given receiver.
        :param receiver_index: Receiver index.
        :param timestamp: New timestamp.
        :param values: New measurement values.
        """
        if self.lengths[receiver_index] == 0:
            self.timestamps[receiver_index] = np.empty((SettingsStore.settings['DECODER_ARRAY_LENGTH'],))
            self.timestamps[receiver_index][0] = timestamp
            self.received[receiver_index] = np.empty((SettingsStore.settings['DECODER_ARRAY_LENGTH'], len(values)))
            self.received[receiver_index][0] = np.array(values)
        else:
            if self.lengths[receiver_index] == len(self.timestamps[receiver_index]):
                self.timestamps[receiver_index] = np.concatenate((self.timestamps[receiver_index], np.empty((SettingsStore.settings['DECODER_ARRAY_LENGTH'],))))
                self.received[receiver_index] = np.vstack((self.received[receiver_index], np.empty((SettingsStore.settings['DECODER_ARRAY_LENGTH'], len(values)))))

            self.timestamps[receiver_index][self.lengths[receiver_index]] = timestamp
            self.received[receiver_index][self.lengths[receiver_index]] = values

        min_timestamp = None
        max_timestamp = None
        for i in range(len(self.timestamps)):
            if self.lengths[i] > 0:
                min_tmp = np.min(self.timestamps[i][:self.lengths[i]])
                max_tmp = np.max(self.timestamps[i][:self.lengths[i]])
                if min_timestamp is None or min_tmp < min_timestamp:
                    min_timestamp = min_tmp
                if max_timestamp is None or max_tmp > max_timestamp:
                    max_timestamp = max_tmp

        self.min_timestamp = min_timestamp if min_timestamp is not None else time.time()
        self.max_timestamp = max_timestamp if max_timestamp is not None else time.time()

    def calculate_additional_datalines(self):
        """
        Calculates additional datalines and stores them in additional datalines.
        Must be a list of dictionaries, where each dictionary must contain ???
        """
        Logging.info("calculate_additional_datalines is not implemented in your selected decoder.", repeat=False)

    def calculate_landmarks(self):
        """
        Calculates landmark positions and stores them in landmarks.
        Must be a list of dictionaries, where each dictionary must contain two lists x and y for the coordinates.
        """
        Logging.info("calculate_landmarks is not implemented in your selected decoder.", repeat=False)

    def calculate_sequence(self):
        """
        Calculates a sequence based on the decoded values and stores it in sequence.
        Must be a list or array.
        """
        Logging.info("calculate_sequence is not implemented in your selected decoder.", repeat=False)

    def calculate_symbol_intervals(self):
        """
        Calculates symbol intervals and stores them in symbol_intervals.
        Must be a list of timestamps (float).
        """
        Logging.info("calculate_symbol_intervals is not implemented in your selected decoder.", repeat=False)

    def calculate_symbol_values(self):
        """
        Calculates symbol values for the symbol intervals.
        Note that symbol_values should be 1 smaller than symbol_intervals.
        Must be a list or array.
        """
        Logging.info("calculate_symbol_values is not implemented in your selected decoder.", repeat=False)

    def check(self):
        """
        Check some potential causes of errors which are checked in every step.
        Might be useful for debugging, but may be ignored during actual usage for better performance.
        """
        # Check landmarks
        if not isinstance(self.landmarks, list):
            Logging.warning("Landmarks is not a list!", repeat=False)
        for landmark in self.landmarks:
            if not len(landmark['x']) == len(landmark['y']):
                Logging.warning("Length of x and y of a landmark do not match!", repeat=False)
                landmark['x'] = landmark['x'][:min(len(landmark['x']), len(landmark['y']))]
                landmark['y'] = landmark['y'][:min(len(landmark['x']), len(landmark['y']))]

        # Check symbol intervals
        if not (isinstance(self.symbol_intervals, list) or isinstance(self.symbol_intervals, np.ndarray)):
            Logging.error("Symbol intervals is not a list or array!", repeat=False)

        # Check symbol values
        if __debug__ and self.symbol_values and not len(self.symbol_values) == len(self.symbol_intervals) - 1:
            Logging.error("Length of symbol_values is not 1 smaller than length of symbol_intervals!", repeat=False)

    def clear(self):
        """
        Clears all data from the decoder and its receivers.
        This is called when the user presses the clear button for the decoder.
        """
        # Clear received
        self.additional_datalines = [None] * self.num_additional_datalines
        self.lengths = [0] * self.num_receivers
        self.received = [None] * self.num_receivers
        self.timestamps = [None] * self.num_receivers
        self.symbol_intervals = []
        self.symbol_values = []
        self.sequence = ""
        self.landmarks = [None] * self.num_landmarks

        for receiver in self.receivers:
            receiver.buffer = []

    def decode(self):
        """
        Main functionality of the decoder that is executed in every step of the main program loop as long as the decode is active.
        It consists of the following steps:
            - Empty receiver buffers.
            - Optionally apply pre-processing.
            - Optionally calculate additional datalines (derivatives, etc.).
            - Optionally calculate landmarks (edges, peaks, etc.).
            - Optionally calculate symbol intervals.
            - Optionally assign value to each symbol interval.
            - Optionally the sequence from the symbol values.
            - If the debug flag is set, perform some error checks.
        """
        self.empty_receiver_buffers()
        self.pre_processing()
        self.calculate_additional_datalines()
        self.calculate_landmarks()
        self.calculate_symbol_intervals()
        self.calculate_symbol_values()
        self.calculate_sequence()

        if __debug__:
            self.check()

    def decoder_removed(self):
        """
        Do stuff when decoder is removed.
        Can be implemented in the decoder implementation.
        """
        pass

    def decoder_stopped(self):
        """
        Do stuff when decoder is stopped.
        Can be implemented in the decoder implementation.
        """
        pass

    def empty_receiver_buffers(self):
        """
        Checks if there is new measurement data in the receiver buffers and possibly stores them in timestamps/values.
        """
        for receiver_index in range(len(self.receivers)):
            available_count = self.receivers[receiver_index].get_available()
            for available in range(available_count):
                measurement = self.receivers[receiver_index].get(0)
                timestamp, values = measurement['timestamp'], measurement['values']
                self.append(receiver_index, timestamp, values)
                self.lengths[receiver_index] += 1

    def export_custom(self, directory):
        """
        Exports received data by creating a new table for every receiver and all additional datalines.
        :param directory: Directory for .csv files to be stored.
        """
        # Export received
        received = self.decoded['received']
        lengths, timestamps, values = received['lengths'], received['timestamps'], received['values']
        for r in range(self.num_receivers):
            filename = os.path.join(directory, "received" + str(r))
            with open(filename, 'w', encoding='UTF8', newline='') as f:
                writer = csv.writer(f)
                for t in range(lengths[r]):
                    row = [timestamps[r][t]] + list(values[r][t, :])
                    writer.writerow(row)

        # Export additional datalines
        additional_datalines = self.decoded['additional_datalines']
        for a in range(len(additional_datalines)):
            filename = os.path.join(directory, "additional_dataline" + str(a))
            dataline = additional_datalines[a]
            length, timestamps, values = dataline['length'], dataline['timestamps'], dataline['values']
            with open(filename, 'w', encoding='UTF8', newline='') as f:
                writer = csv.writer(f)
                for i in length:
                    row = [timestamps[i], values[i]]
                    writer.writerow(row)

    def export_sequence(self, filename):
        """
        Export decoded sequence to file.
        :param filename: Destination path.
        """
        if not filename == "":
            with open(filename, 'w') as file:
                file.write(self.sequence)

    def export_symbol_values(self, filename):
        """
        Export decoded symbol values to file.
        :param filename: Destination path.
        """
        if not filename == "":
            with open(filename, 'w') as file:
                symbol_values_str = str(self.symbol_values)
                symbol_values_str = symbol_values_str.replace("[", "").replace("]", "").replace("'", "").replace(" ", "")
                file.write(symbol_values_str)

    def get_decoded(self):
        """
        Returns current decoder values.
        :return: Current decoder values.
        """
        self.decoded = {
            'received': {
                'lengths': self.lengths,
                'timestamps': self.timestamps,
                'values': self.received
            },
            'additional_datalines': self.additional_datalines,
            'landmarks': self.landmarks,
            'min_timestamp': self.min_timestamp,
            'max_timestamp': self.max_timestamp,
            'symbol_intervals': self.symbol_intervals,
            'symbol_values': self.symbol_values,
            'sequence': self.sequence
        }
        return self.decoded

    def get_received(self, receiver_index, sensor_index=-1):
        """
        Gets receiver values.
        :param receiver_index: Index of desired receiver.
        :param sensor_index: Index of desired sensor, set to -1 to get all sensor values.
        :return: Received values, dimensions (time, sensors) or (time).
        """
        received = self.decoded['received']
        lengths, timestamps, values = received['lengths'], received['timestamps'], received['values']
        if lengths[0] == 0:
            return None
        return values[receiver_index][:lengths[receiver_index], :] if sensor_index == -1 else values[receiver_index][:lengths[receiver_index], sensor_index]

    def parameters_edited(self):
        """
        Do stuff when the parameters are edited by the user.
        May be overriden in the concrete implementation.
        """
        pass

    def pre_processing(self):
        """
        Pre-process input from receivers, e.g., apply filters.
        """
        Logging.info("pre_processing is not implemented in your selected decoder.", repeat=False)

    def start(self):
        """
        Starts the decoder.
        Runs the listen function of the receiver in a new (daemon) thread.
        """
        for receiver_index in range(self.num_receivers):
            self.receivers[receiver_index].running = True
            thread = threading.Thread(target=self.receivers[receiver_index].listen, daemon=True)
            thread.start()
        self.active = True

    def stop(self):
        """
        Stops the decoder.
        """
        self.active = False
        for receiver in self.receivers:
            receiver.running = False
        self.decoder_stopped()