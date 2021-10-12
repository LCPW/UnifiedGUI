import time


class ReceiverInterface:
    def __init__(self, description, num_sensors, sensor_descriptions):
        self.description = description
        self.num_sensors = num_sensors
        self.sensor_descriptions = sensor_descriptions
        self.buffer = []

    def get_available(self):
        x = len(self.buffer)
        return x

    def get(self, idx):
        return self.buffer.pop(idx)

    def append_values(self, values):
        timestamp = time.time()
        self.buffer.append({'timestamp': timestamp, 'values': values})