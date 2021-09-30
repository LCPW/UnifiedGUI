from Models import Decoder, ExampleReceiver

import threading


class ExampleDecoder(Decoder.Decoder):
    def __init__(self):
        super().__init__()
        self.num_receivers = 2

        self.received = []
        self.decoded = []

        self.receiver = ExampleReceiver.ExampleReceiver()
        thread_receiver = threading.Thread(target=self.receiver.listen)
        thread_receiver.start()

    def get_num_receivers(self):
        return self.num_receivers

    def get_received(self):
        return self.received

    def get_decoded(self):
        self.get_values()
        return self.decoded

    def get_values(self):
        n = self.receiver.get_available()
        for i in range(0, n):
            self.received.append(self.receiver.get(i))

        self.decoded = []
        for i in range(0, len(self.received)):
            t, x = self.received[i]

            if x < 0.5:
                self.decoded.append((t, "A"))
            else:
                self.decoded.append((t, "B"))

