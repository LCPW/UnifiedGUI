from Models.Interfaces.ReceiverInterface import ReceiverInterface
import time
import random


class ExampleReceiver(ReceiverInterface):
    def __init__(self, description):
        self.description = description
        self.num_sensors = 2
        self.sensor_descriptions = ["Value1", "Value2"]
        super().__init__(self.description, self.num_sensors, self.sensor_descriptions)

        #self.value1 = random.random()
        #self.value2 = random.random()

    def listen(self):
        while True:
            time.sleep(0.001)
            value1 = random.random()
            value2 = random.random()
            values = (value1, value2)
            # values = (self.value1, self.value2)
            self.append_values(values)

