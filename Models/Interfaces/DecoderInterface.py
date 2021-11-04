import importlib
import threading
import numpy as np

import Logging


class DecoderInterface:
    def __init__(self, num_receivers, receiver_types, receiver_descriptions=None, landmark_names=None, landmark_symbols=None):
        self.num_receivers = len(receiver_types)
        #self.receiver_types = receiver_types
        #assert self.num_receivers == len(self.receiver_types), "num_receivers not equal to length of receiver_types."
        self.receiver_descriptions = [str(receiver_types[i]) + str(i+1) for i in range(len(self.receiver_types))] if receiver_descriptions is None else receiver_descriptions
        self.num_landmarks = 0 if landmark_names is None else len(landmark_names)
        self.landmark_names = [] if landmark_names is None else landmark_names
        self.landmark_symbols = landmark_symbols
        if __debug__ and not len(self.landmark_symbols) == self.num_landmarks:
            Logging.log("Length of landmark symbols does not match number of landmarks", 'WARNING')
            self.landmark_symbols = None

        self.active = False

        self.receivers = []
        self.receiver_buffer = []

        self.timestamps = []
        self.received = []

        for receiver_index in range(self.num_receivers):
            # Dynamically import the module of the implementation
            module = importlib.import_module('.' + self.receiver_types[receiver_index], package='Models.Implementations.Receivers')
            # Create an instance of the class in the said module (e.g. ExampleReceiver.ExampleReceiver())
            instance = getattr(module, self.receiver_types[receiver_index])(self.receiver_descriptions[receiver_index])
            self.receivers.append(instance)
            self.receiver_buffer.append([])

            self.timestamps.append(None)
            self.received.append(None)

        self.landmarks = []
        for landmark_index in range(self.num_landmarks):
            self.landmarks.append(None)
        self.symbol_intervals = []
        self.symbol_values = []
        self.sequence = ""

    def start(self):
        """
        Runs the listen function of the receiver in a new (daemon) thread.
        """
        for receiver_index in range(self.num_receivers):
            thread = threading.Thread(target=self.receivers[receiver_index].listen, daemon=True)
            thread.start()
        self.active = True

    def stop(self):
        # TODO: Stop threads?
        self.active = False

    def get_receiver_info(self):
        receiver_info = []
        for receiver in self.receivers:
            receiver_info.append({'description': receiver.description, 'sensor_descriptions': receiver.sensor_descriptions})
        return receiver_info

    def get_landmark_info(self):
        return {'num': self.num_landmarks, 'names': self.landmark_names, 'symbols': self.landmark_symbols}

    def get_decoded(self):
        #self.decode()
        received = {'timestamps': self.timestamps, 'values': self.received}
        return {'received': received, 'landmarks': self.landmarks, 'symbol_intervals': self.symbol_intervals, 'symbol_values': self.symbol_values, 'sequence': self.sequence}

    def append_timestamp(self, index, timestamp):
        if self.timestamps[index] is None:
            self.timestamps[index] = np.array([timestamp])
        else:
            self.timestamps[index] = np.append(self.timestamps[index], timestamp)

    def append_values(self, index, values):
        if self.received[index] is None:
            self.received[index] = np.empty((1, len(values)))
            self.received[index][0] = np.array(values)
        else:
            self.received[index] = np.vstack((self.received[index], np.array(values)))

    def empty_receiver_buffers(self):
        #print(threading.current_thread().name)
        for i in range(len(self.receivers)):
            n = self.receivers[i].get_available()
            for j in range(n):
                x = self.receivers[i].get(0)
                timestamp, values = x['timestamp'], x['values']
                # TODO: This can be problematic since for a short amount of time, timestamps and values does not have the same length
                self.append_timestamp(i, timestamp)
                self.append_values(i, values)

    def calculate_symbol_intervals(self):
        """
        Calculates symbol intervals and stores them in symbol_intervals.
        Must be a list of timestamps (float).
        """
        # TODO: Logging
        print("Hint: calculate_symbol_intervals is not implemented in your selected decoder.")

    def calculate_symbol_values(self):
        """
        Calculates symbol values for the symbol intervals.
        Note that symbol_values should be 1 smaller than symbol_intervals.
        Must be a list or array.
        """
        # TODO: Logging
        print("Hint: calculate_symbol_values is not implemented in your selected decoder.")

    def calculate_landmarks(self):
        # TODO: Logging
        print("Hint: calculate_landmarks not not implemented in your selected decoder.")

    def calculate_sequence(self):
        # TODO: Logging
        pass

    def decode(self):
        """
        Main functionality of the decoder that is executed in every step of the main program loop.
        """

        self.empty_receiver_buffers()
        # Optionally apply filter

        # Optionally calculate landmarks (edges, peaks, etc.)
        self.calculate_landmarks()
        if __debug__ and not isinstance(self.landmarks, list):
            Logging.log("Landmarks is not a list.", 'WARNING')

        # Calculate symbol intervals
        self.calculate_symbol_intervals()
        if __debug__ and not (isinstance(self.symbol_intervals, list) or isinstance(self.symbol_intervals, np.ndarray)):
            Logging.log("Symbol intervals is not a list or array", 'WARNING')

        # Assign value to each symbol interval
        self.calculate_symbol_values()
        # If list is non-empty and ...
        if __debug__ and self.symbol_values and not len(self.symbol_values) == len(self.symbol_intervals) - 1:
            Logging.log("Length of symbol_values is not 1 smaller than length of symbol_intervals", 'WARNING')

        # Calculate the sequence from the symbol values
        self.calculate_sequence()