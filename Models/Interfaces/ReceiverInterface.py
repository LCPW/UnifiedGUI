import time
from Utils import Logging


class ReceiverInterface:
    def __init__(self, name):
        self.name = name
        self.num_sensors = None
        self.sensor_names = None
        self.buffer = []

    def setup(self):
        if self.sensor_names is None:
            Logging.info("No sensor names provided, automatically generating them.")
            self.sensor_names = ["Sensor" + str(i + 1) for i in range(self.num_sensors)]
        if len(self.sensor_names) != self.num_sensors:
            Logging.warning("Sensor names do not match number of sensors!")
            self.sensor_names = ["Sensor" + str(i + 1) for i in range(self.num_sensors)]

    def get_available(self):
        """
        Get how many measurements are available in the buffer.
        :return: length of the buffer.
        """
        return len(self.buffer)

    def get(self, idx):
        """
        Removes and returns a measurement of the buffer.
        :param idx: index of the measurement to be removed from the buffer.
        :return: removed measurement.
        """
        return self.buffer.pop(idx)

    def append_values(self, values, timestamp=None):
        """
        Appends values to the buffer with a timestamp.
        :param values: values to be appended, should be list or tuple.
        :param timestamp: timestamp when the values were measured, if None, current time is used.
        """
        if not (isinstance(values, list) or isinstance(values, tuple)):
            Logging.warning("Values are not a tuple or list, check your implementation of append_values.", repeat=False)
            values = [values]

        if timestamp is None:
            # Get current timestamp
            timestamp = time.time()
        self.buffer.append({'timestamp': timestamp, 'values': values})