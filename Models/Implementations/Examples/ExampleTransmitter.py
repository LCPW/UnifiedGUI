import time

from Models.Interfaces.TransmitterInterface import TransmitterInterface
from Utils import Queue


class ExampleTransmitter(TransmitterInterface):
    def __init__(self, initial_value):
        super().__init__()
        self.value = initial_value

        self.num_channels = 1
        self.channel_names = ["CH" + str(i) for i in range(self.num_channels)]

    def transmit_step(self):
        timestamp = time.time()
        Queue.queue.put((self.value, timestamp))