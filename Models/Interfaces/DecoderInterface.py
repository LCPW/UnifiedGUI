import importlib
import threading
import numpy as np

import Logging


class DecoderInterface:
    def __init__(self, parameters, parameter_values):
        self.parameters = parameters
        self.parameter_values = parameter_values

        # Mandatory
        self.receiver_types = None

        # Optional
        self.receiver_descriptions = None
        self.landmark_names = None
        self.landmark_symbols = None

    def setup(self):
        self.num_receivers = len(self.receiver_types)

        if self.receiver_descriptions is None:
            Logging.info("No receiver descriptions provided, automatically generating them.")
            self.receiver_descriptions = [str(self.receiver_types[i]) + str(i+1) for i in range(self.num_receivers)]

        if self.landmark_names is None:
            self.landmark_names = []
            self.num_landmarks = 0
        else:
            self.num_landmarks = len(self.landmark_names)
            if self.landmark_symbols is None:
                Logging.info("No landmark symbols provided, using circle as default symbol.")
                self.landmark_symbols = ['o'] * self.num_landmarks
            elif not len(self.landmark_symbols) == self.num_landmarks:
                Logging.warning("Length of landmark symbols does not match number of landmarks!")
                self.landmark_symbols = ['o'] * self.num_landmarks

        self.active = False

        self.receivers = []
        self.receiver_buffer = []

        self.timestamps = []
        self.received = []

        for receiver_index in range(self.num_receivers):
            # Dynamically import the module of the implementation
            module = importlib.import_module('.' + self.receiver_types[receiver_index], package='Models.Implementations.Receivers')
            # Create an instance of the class in the said module (e.g. ExampleReceiver.ExampleReceiver())
            receiver = getattr(module, self.receiver_types[receiver_index])(self.receiver_descriptions[receiver_index])
            receiver.setup()
            self.receivers.append(receiver)
            self.receiver_buffer.append([])

            self.timestamps.append(None)
            self.received.append(None)

        self.landmarks = []
        for landmark_index in range(self.num_landmarks):
            self.landmarks.append(None)
        self.symbol_intervals = []
        self.symbol_values = []
        self.sequence = ""

        self.decoded = None

    def start(self):
        """
        Runs the listen function of the receiver in a new (daemon) thread.
        """
        for receiver_index in range(self.num_receivers):
            thread = threading.Thread(target=self.receivers[receiver_index].listen, daemon=True)
            thread.start()
        self.active = True

    def stop(self):
        self.active = False

    def get_receiver_info(self):
        receiver_info = []
        for receiver in self.receivers:
            receiver_info.append({'description': receiver.description, 'sensor_descriptions': receiver.sensor_descriptions})
        return receiver_info

    def get_landmark_info(self):
        return {'num': self.num_landmarks, 'names': self.landmark_names, 'symbols': self.landmark_symbols}

    def get_decoded(self):
        received = {'timestamps': self.timestamps, 'values': self.received}
        self.decoded = {'received': received, 'landmarks': self.landmarks, 'symbol_intervals': self.symbol_intervals, 'symbol_values': self.symbol_values, 'sequence': self.sequence}
        return self.decoded

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
        Logging.info("calculate_symbol_intervals is not implemented in your selected decoder.", repeat=False)

    def calculate_symbol_values(self):
        """
        Calculates symbol values for the symbol intervals.
        Note that symbol_values should be 1 smaller than symbol_intervals.
        Must be a list or array.
        """
        Logging.info("calculate_symbol_values is not implemented in your selected decoder.", repeat=False)

    def calculate_landmarks(self):
        Logging.info("calculate_landmarks is not implemented in your selected decoder.", repeat=False)

    def calculate_sequence(self):
        Logging.info("calculate_sequence is not implemented in your selected decoder.", repeat=False)

    def decode(self):
        """
        Main functionality of the decoder that is executed in every step of the main program loop as long as the decode is active.
        """
        # 1. Empty receive buffers
        self.empty_receiver_buffers()

        # 2. Optionally apply filter

        # 3. Optionally calculate landmarks (edges, peaks, etc.)
        self.calculate_landmarks()

        # 4. Calculate symbol intervals
        self.calculate_symbol_intervals()

        # 5. Assign value to each symbol interval
        self.calculate_symbol_values()

        # 6. Calculate the sequence from the symbol values
        self.calculate_sequence()

        if __debug__:
            self.check()

    def check(self):
        # 3. Check landmarks
        if not isinstance(self.landmarks, list):
            Logging.warning("Landmarks is not a list!", repeat=False)
        for landmark in self.landmarks:
            if not len(landmark['x']) == len(landmark['y']):
                Logging.warning("Length of x and y of a landmark do not match!", repeat=False)
                landmark['x'] = landmark['x'][:min(len(landmark['x']), len(landmark['y']))]
                landmark['y'] = landmark['y'][:min(len(landmark['x']), len(landmark['y']))]

        # 4. Check symbol intervals
        if not (isinstance(self.symbol_intervals, list) or isinstance(self.symbol_intervals, np.ndarray)):
            Logging.warning("Symbol intervals is not a list or array!", repeat=False)

        # 5. Check symbol values
        if __debug__ and self.symbol_values and not len(self.symbol_values) == len(self.symbol_intervals) - 1:
            Logging.warning("Length of symbol_values is not 1 smaller than length of symbol_intervals!", repeat=False)