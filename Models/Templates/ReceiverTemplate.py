"""
Author:
E-mail:
"""

from Models.Interfaces.ReceiverInterface import ReceiverInterface


class ExampleReceiver(ReceiverInterface):
    def __init__(self):
        super().__init__()

        # Implement: Define number of sensors
        self.num_sensors = None

        super().setup()

    def listen_step(self):
        # Implement: Listen for new measurement values
        pass