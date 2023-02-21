import numpy as np

from Models.Interfaces.EncoderInterface import EncoderInterface
from Models.Implementations.Examples.ExampleTransmitter import ExampleTransmitter


class ExampleEncoder(EncoderInterface):
    def __init__(self, parameters, parameter_values):
        super().__init__(parameters, parameter_values)
        self.transmitters = [ExampleTransmitter(0)]
        self.allowed_sequence_values = [chr(i) for i in range(0, 128)]
        self.sleep_time = parameter_values['Sleep time [s]']

        super().setup()

    def encode(self, sequence):
        symbol_values = ""
        for s in sequence:
            c = ord(s)
            r = ""
            while True:
                div = c / 2
                # 0, Rest 0
                if div == 0:
                    break
                # 0, Rest 1
                elif div < 1:
                    r += '1'
                    break
                # X, Rest 0
                elif div.is_integer():
                    r += '0'
                # X, Rest 1
                else:
                    r += '1'
                c = int(np.floor(div))
            x = ((7-len(r)) * '0') + r[::-1]
            symbol_values += x
        y = []
        for s in symbol_values:
            y += [int(s) + 1]
            y += [0]
        symbol_values = y + [-1, 0]
        return symbol_values

    def parameters_edited(self):
        self.sleep_time = self.parameter_values['Sleep time [s]']

    def transmit_single_symbol_value(self, symbol_value):
        self.transmitters[0].value = int(symbol_value)


def get_parameters():
    parameters = [
        {
            'description': "Sleep time [s]",
            'decimals': 3,
            'dtype': 'float',
            'min': 0,
            'max': 100,
            'default': 0.1,
        }
    ]
    return parameters