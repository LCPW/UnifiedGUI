from Models.Interfaces.ReceiverInterface import ReceiverInterface
import time
from datetime import datetime
import random


class ExampleReceiver(ReceiverInterface):
    def __init__(self):
        super().__init__()
        self.buffer = []

    def listen(self):
        while True:
            time.sleep(1)
            x = random.random()
            t = datetime.now()
            self.buffer.append((t, x))

    def get_available(self):
        return len(self.buffer)

    def get(self, idx):
        return self.buffer.pop(idx)

