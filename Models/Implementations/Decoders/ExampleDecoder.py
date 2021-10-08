from Models.Interfaces.DecoderInterface import DecoderInterface


class ExampleDecoder(DecoderInterface):
    def __init__(self):
        self.num_receivers = 3
        self.receiver_types = ["ExampleReceiver"] * self.num_receivers
        self.receiver_descriptions = ["ExampleReceiver1", "ExampleReceiver2", "ExampleReceiver3"]
        # The receiver descriptions are optional
        super().__init__(self.num_receivers, self.receiver_types, receiver_descriptions=self.receiver_descriptions)