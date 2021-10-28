from Models.Interfaces.DecoderInterface import DecoderInterface


class ExampleDecoder(DecoderInterface):
    def __init__(self):
        self.num_receivers = 3
        self.receiver_types = ["ExampleReceiver"] * self.num_receivers
        self.receiver_descriptions = None
        # self.receiver_descriptions = ["ExampleReceiver1", "ExampleReceiver2", "ExampleReceiver3"]
        # The receiver descriptions are optional
        super().__init__(self.num_receivers, self.receiver_types, receiver_descriptions=self.receiver_descriptions)

    def calculate_symbol_intervals(self):
        if self.timestamps[0] is not None:
            self.symbol_intervals = self.timestamps[0][::50]

    def calculate_symbol_values(self):
        x = len(self.symbol_intervals) - 1
        self.symbol_values = ["0"] * x
        #for i in range(len(self.symbol_values), len(self.symbol_intervals - 1)):
        #    self.symbol_values.append("0")