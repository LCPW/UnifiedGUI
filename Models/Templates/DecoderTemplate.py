"""
Author:
E-mail:
"""

from Models.Interfaces.DecoderInterface import DecoderInterface


class ExampleDecoder(DecoderInterface):
    def __init__(self, parameters, parameter_values):
        super().__init__(parameters, parameter_values)

        # Implement: Define receivers list
        self.receivers = None

        super().setup()


def get_parameters():
    return None