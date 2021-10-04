from Models import Decoder, ExampleReceiver

import threading


class ExampleDecoder(Decoder.Decoder):
    def __init__(self):
        self.num_receivers = 2
        self.receiver_types = ["ExampleReceiver", "ExampleReceiver"]
        super().__init__(self.num_receivers)

    def start(self):
        for i in range(self.num_receivers):
            self.receivers.append(ExampleReceiver.ExampleReceiver())
            self.receiver_buffer.append([])
            thread = threading.Thread(target=self.receivers[i].listen)
            thread.start()
        self.active = True