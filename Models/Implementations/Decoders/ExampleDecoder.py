from Models.Interfaces.DecoderInterface import DecoderInterface


class ExampleDecoder(DecoderInterface):
    def __init__(self):
        self.num_receivers = 3
        self.receiver_types = ["ExampleReceiver"] * self.num_receivers
        super().__init__(self.num_receivers, self.receiver_types)