from Models.Interfaces.DecoderInterface import DecoderInterface


class ExampleDecoder(DecoderInterface):
    def __init__(self, parameter_values):
        super().__init__(parameter_values)

        # Implement: Define receivers list
        self.receiver_types = None

        super().setup()


def get_parameters():
    return None