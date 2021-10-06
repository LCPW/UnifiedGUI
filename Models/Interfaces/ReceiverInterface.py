from datetime import datetime


class ReceiverInterface:
    def __init__(self, description, num_sensors, sensor_descriptions):
        self.description = description
        self.num_sensors = num_sensors + 1
        self.sensor_descriptions = ["Timestamp"] + sensor_descriptions
        self.buffer = []

    def get_available(self):
        return len(self.buffer)

    def get(self, idx):
        return self.buffer.pop(idx)

    def append_value(self, values):
        timestamp = datetime.now()
        self.buffer.append((timestamp,) + values)