from Models.Interfaces.ReceiverInterface import ReceiverInterface
import time
import random


class ExampleReceiver(ReceiverInterface):
    def __init__(self):
        self.description = "ExampleReceiver"
        self.num_sensors = 2
        self.sensor_descriptions = ["Value1", "Value2"]
        super().__init__(self.description, self.num_sensors, self.sensor_descriptions)

    def listen(self):
        while True:
            time.sleep(1)
            value1 = random.random()
            value2 = random.random()
            values = (value1, value2)
            self.append_value(values)

