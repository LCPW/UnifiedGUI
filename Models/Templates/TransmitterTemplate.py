from Models.Interfaces.TransmitterInterface import TransmitterInterface


class ExampleTransmitter(TransmitterInterface):
    def __init__(self):
        super().__init__()

    def transmit_step(self):
        # Implement: Run a single step of the transmitter
        pass