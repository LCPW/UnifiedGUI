import numpy as np

from Models.Interfaces.DecoderInterface import DecoderInterface
from Models.Implementations.Examples.ExampleReceiver import ExampleReceiver


class ExampleDecoder(DecoderInterface):
    def __init__(self, parameters, parameter_values):
        super().__init__(parameters, parameter_values)

        self.receivers = [ExampleReceiver()]

        super().setup()

    def calculate_symbol_intervals(self):
        l = self.lengths[0]
        if l > 0:
            difference = self.received[0][1:l] - self.received[0][0:l-1]
            indices = list(np.nonzero(np.array(difference))[0])
            self.symbol_intervals = [self.timestamps[0][i] for i in indices]

    def calculate_symbol_values(self):
        for i in range(len(self.symbol_values), len(self.symbol_intervals) - 1):
            left_index = np.argmin(list(map(abs, self.timestamps[0][:self.lengths[0]] - self.symbol_intervals[i])))
            right_index = np.argmin(list(map(abs, self.timestamps[0][:self.lengths[0]] - self.symbol_intervals[i + 1])))

            max_tmp = int(np.round(np.mean(self.received[0][left_index:right_index])))
            self.symbol_values += [max_tmp]

    def calculate_sequence(self):
        symbol_length = 7
        length = max(0, len(self.symbol_values) - symbol_length * 2)
        for i in range(len(self.sequence) * symbol_length * 2, length, symbol_length * 2):
            vs = self.symbol_values[i:i + symbol_length * 2]
            vs = [v-1 for v in vs if v > 0]
            c = 0
            for bit in vs:
                c = c * 2 + bit
            self.sequence += chr(c)


def get_parameters():
    return None