import importlib
import threading
import numpy as np


class DecoderInterface:
    def __init__(self, num_receivers, receiver_types, receiver_descriptions=None, landmark_names=None):
        self.num_receivers = num_receivers
        self.receiver_types = receiver_types
        self.receiver_descriptions = [str(receiver_types[i]) + str(i+1) for i in range(len(self.receiver_types))] if receiver_descriptions is None else receiver_descriptions
        self.num_landmarks = 0 if landmark_names is None else len(landmark_names)
        self.landmark_names = landmark_names

        self.active = False

        self.receivers = []
        self.receiver_buffer = []

        self.timestamps = []
        self.received = []

        for i in range(self.num_receivers):
            # Dynamically import the module of the implementation
            module = importlib.import_module('.' + self.receiver_types[i], package='Models.Implementations.Receivers')
            # Create an instance of the class in the said module (e.g. ExampleReceiver.ExampleReceiver())
            instance = getattr(module, self.receiver_types[i])(self.receiver_descriptions[i])
            self.receivers.append(instance)
            self.receiver_buffer.append([])

            self.timestamps.append(None)
            self.received.append(None)

        # TODO
        self.landmarks = []
        for i in range(self.num_landmarks):
            self.landmarks.append(None)
        self.symbol_intervals = []
        self.symbol_values = []

    def start(self):
        for i in range(self.num_receivers):
            thread = threading.Thread(target=self.receivers[i].listen, daemon=True)
            thread.start()
        self.active = True

    def stop(self):
        # TODO: Stop threads?
        self.active = False

    def get_num_receivers(self):
        return self.num_receivers

    def get_receiver_info(self):
        receiver_info = []
        for receiver in self.receivers:
            receiver_info.append({'description': receiver.description, 'sensor_descriptions': receiver.sensor_descriptions})
        return receiver_info

    def get_landmark_info(self):
        # TODO: No landmarks
        return {'names': self.landmark_names}

    def is_active(self):
        return self.active

    def get_decoded(self):
        self.decode()
        received = {'timestamps': self.timestamps, 'values': self.received}
        return {'received': received, 'landmarks': self.landmarks, 'symbol_intervals': self.symbol_intervals, 'symbol_values': self.symbol_values}

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
        # print(threading.current_thread().name)
        for i in range(len(self.receivers)):
            n = self.receivers[i].get_available()
            for j in range(n):
                # self.receiver_buffer[i].append(self.receivers[i].get(0))
                x = self.receivers[i].get(0)
                timestamp, values = x['timestamp'], x['values']
                self.append_timestamp(i, timestamp)
                self.append_values(i, values)

    def calculate_symbol_intervals(self):
        # TODO
        print("Hint: calculate_symbol_intervals is not implemented in your selected decoder.")

    def calculate_symbol_values(self):
        # TODO
        print("Hint: calculate_symbol_values is not implemented in your selected decoder.")

    def calculate_landmarks(self):
        # TODO
        print("Hint: calculate_landmarks not not implemented in your selected decoder.")

    def decode(self):
        # TODO
        self.empty_receiver_buffers()
        # Optionally apply filter
        # Optionally calculate landmarks (edges, peaks, etc.)
        self.calculate_landmarks()
        # Calculate symbol intervals
        self.calculate_symbol_intervals()
        # Assign value to each symbol interval
        self.calculate_symbol_values()