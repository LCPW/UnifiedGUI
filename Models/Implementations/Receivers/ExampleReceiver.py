from Models.Interfaces.ReceiverInterface import ReceiverInterface
import time
import random


class ExampleReceiver(ReceiverInterface):
    def __init__(self):
        super().__init__()

        self.num_sensors = 2
        self.sensor_names = ["Sensor A", "Sensor B"]

        self.value1 = random.random()
        self.value2 = random.random()

        self.i = 0

        super().setup()

    def listen(self):
        while self.running:
            time.sleep(0.001)
            # value1 = self.value1 + 0.1 * random.random()
            # value2 = self.value2 + 0.1 * random.random()
            value1, value2 = self.value1 + self.i, self.value2 + self.i
            self.i += 0.001
            values = (value1, value2)
            # values = [value1, value2]
            # values = (self.value1, self.value2)
            self.append_values(values)