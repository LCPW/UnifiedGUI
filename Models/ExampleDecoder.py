from Models import Decoder, ExampleReceiver

import threading


class ExampleDecoder(Decoder.Decoder):
    def __init__(self):
        super().__init__()

        self.received = []
        self.buffer = []

        self.receiver = ExampleReceiver.ExampleReceiver()
        thread_receiver = threading.Thread(target=self.receiver.listen)
        thread_receiver.start()

    def get_received(self):
        return self.received

    def get_values(self):
        n = self.receiver.get_available()
        for i in range(0, n):
            self.received.append(self.receiver.get(i))

        self.buffer = []
        for i in range(0, len(self.received)):
            t, x = self.received[i]

            if x < 0.5:
                self.buffer.append((t, "A"))
            else:
                self.buffer.append((t, "B"))

    def get_available(self):
        self.get_values()
        return len(self.buffer)

    # def pop(self, idx):
    #     return self.buffer.pop(idx)

    def get_decoded(self):
        self.get_values()
        return self.buffer