from Models.Interfaces.DecoderInterface import DecoderInterface


class ExampleDecoder(DecoderInterface):
    def __init__(self):
        self.num_receivers = 2
        self.receiver_types = ["ExampleReceiver", "ExampleReceiver"]
        super().__init__(self.num_receivers, self.receiver_types)

