from datetime import datetime


class ReceiverInterface:
    def __init__(self, description, num_sensors, sensor_descriptions):
        self.description = description
        self.num_sensors = num_sensors
        self.sensor_descriptions = sensor_descriptions
        self.buffer = []

    def get_available(self):
        return len(self.buffer)

    def get(self, idx):
        return self.buffer.pop(idx)

    def append_values(self, values):
        timestamp = datetime.now()
        self.buffer.append({'timestamp': timestamp, 'values': values})