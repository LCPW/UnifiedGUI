from Models.Interfaces.EncoderInterface import EncoderInterface


class ExampleEncoder(EncoderInterface):
    def __init__(self, parameters, parameter_values):
        super().__init__(parameters, parameter_values)

        # Implement: Define transmitters list
        self.transmitters = None

        # Optional
        # self.allowed_sequence_values = None
        # self.sleep_time = None

        super().setup()

    def encode(self, sequence):
        # Implement: Convert sequence to a list of symbol values
        pass

    def parameters_edited(self):
        pass

    def transmit_single_symbol_value(self, symbol_value):
        # Implement: Transmit a single symbol value
        pass


def get_parameters():
    return None