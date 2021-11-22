from Models.Interfaces.ReceiverInterface import ReceiverInterface


class ExampleReceiver(ReceiverInterface):
    def __init__(self, description):
        super().__init__(description)

        # Implement: Define number of sensors
        self.num_sensors = None

    def setup(self):
        super().setup()

    def listen(self):
        while True:
            # Implement: Read measurement values
            values = None
            self.append_values(values)