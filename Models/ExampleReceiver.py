from Models import Receiver
import time
from datetime import datetime
import random


class ExampleReceiver(Receiver.Receiver):
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

