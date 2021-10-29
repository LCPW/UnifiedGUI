from Models.Interfaces.ReceiverInterface import ReceiverInterface


class ExampleReceiver(ReceiverInterface):
    def __init__(self, description):
        # TODO
        # self.num_sensors =
        # self.sensor_descriptions = ["Value1", "Value2"]
        super().__init__(description, self.num_sensors, self.sensor_descriptions)

    def listen(self):
        while True:
            # TODO
            # values = (a, b)
            # self.append_values(values)
            pass
