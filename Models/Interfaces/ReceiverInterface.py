import time


class ReceiverInterface:
    def __init__(self, description, num_sensors, sensor_descriptions=None):
        self.description = description
        self.num_sensors = num_sensors
        if sensor_descriptions is None or len(sensor_descriptions) != self.num_sensors:
            self.sensor_descriptions = ["Value" + str(i + 1) for i in range(num_sensors)]
        else:
            self.sensor_descriptions = sensor_descriptions
        self.buffer = []

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
            print("Values are not a tuple or list, check your implementation of append_values.")
            values = [values]

        # Get current timestamp
        if timestamp is None:
            timestamp = time.time()
        self.buffer.append({'timestamp': timestamp, 'values': values})