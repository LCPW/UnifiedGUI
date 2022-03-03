from Models.Interfaces.DecoderInterface import DecoderInterface
import random
import time


class ExampleDecoder(DecoderInterface):
    def __init__(self, parameters, parameter_values):
        super().__init__(parameters, parameter_values)
        # Mandatory
        self.receiver_types = ["ExampleReceiver"] * 3

        # Optional
        self.receiver_names = ["Alpha", "Beta", "Gamma"]
        self.landmark_names = ['Landmark1', 'Landmark2']

        self.plot_settings = {
            'datalines_active': [[True, False], [False, True], [True, False]],
            'datalines_width': 1,
            '#datalines_style': [],
            'landmarks_active': [True, False],
            'landmarks_size': 15,
            'landmarks_symbols': ['x', 'd'],
            'step_size': 1,
            'symbol_intervals': True,
            'symbol_intervals_color': 'k',
            'symbol_intervals_width': 1,
            'symbol_values_fixed_height': 1,
            'symbol_values_position': 'above',
            'symbol_values_size': 20,
            'symbol_values': True,
            'symbol_values_height_factor': 1.1
        }

        super().setup()

    def calculate_symbol_intervals(self):
        if not self.symbol_intervals:
            self.symbol_intervals = [time.time()]
        else:
            t = time.time()
            if t - self.symbol_intervals[-1] > 1:
                self.symbol_intervals.append(t)

    def calculate_symbol_values(self):
        x = len(self.symbol_intervals) - 1
        r = random.random()
        for i in range(len(self.symbol_values), x):
            y = 0 if r < 0.5 else 1
            self.symbol_values.append(y)

    def calculate_landmarks(self):
        x = [0.5 * (self.symbol_intervals[a] + self.symbol_intervals[a+1]) for a in range(max(0, len(self.symbol_intervals) - 1))]
        y = [self.received[0][i, 0] for i in range(len(x))]
        for i in range(self.num_landmarks):
            self.landmarks[i] = {'x': x, 'y': [a/(2**i) for a in y]}

    def calculate_sequence(self):
        length = max(0, len(self.symbol_values) - 4)
        for i in range(len(self.sequence) * 4, length, 4):
            vs = self.symbol_values[i:i+4]
            c = 0
            for bit in vs:
                c = c * 2 + bit
            c += 65
            self.sequence += chr(c)


def get_parameters():
    parameters = [
        {
            'description': "Parameter1",
            'decimals': 4,
            'dtype': 'float',
            'min': 0,
            'max': 100,
            'default': 50,
        },
        {
            'description': "Parameter2",
            'dtype': 'bool',
            'default': True
        },
        {
            'description': "Parameter3",
            'dtype': 'item',
            'items': ['A', 'B', 'C'],
            'default': 'B'
        },
        {
            'description': "Parameter4",
            'dtype': 'int',
            'min': 0,
            'max': 100,
            'default': 25,
        },
        {
            'description': "Parameter5",
            'dtype': 'string',
            'default': "Hello World",
            'max_length': 20
        }
    ]
    return parameters