import time


class ReceiverInterface:
    def __init__(self, description, num_sensors, sensor_descriptions=None):
        self.description = description
        self.num_sensors = num_sensors
        self.sensor_descriptions = ["Value" + str(i) for i in range(num_sensors)] if sensor_descriptions is None else sensor_descriptions
        self.buffer = []

    def get_available(self):
        x = len(self.buffer)
        return x

    def get(self, idx):
        return self.buffer.pop(idx)

    def append_values(self, values):
        timestamp = time.time()
        self.buffer.append({'timestamp': timestamp, 'values': values})