from Models.Interfaces.DecoderInterface import DecoderInterface
import random

PARAMETERS = [
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


class ExampleDecoder(DecoderInterface):
    def __init__(self, parameters, parameter_values):
        super().__init__(parameters, parameter_values)
        # Mandatory
        self.receiver_types = ["ExampleReceiver"] * 3

        # Optional
        self.landmark_names = ['Test1', 'Test2']
        self.landmark_symbols = ['x', 'd']

    def setup(self):
        super().setup()

    def calculate_symbol_intervals(self):
        if self.timestamps[0] is not None:
            self.symbol_intervals = self.timestamps[0][::50]

    def calculate_symbol_values(self):
        x = len(self.symbol_intervals) - 1
        r = random.random()
        for i in range(len(self.symbol_values), x):
            y = 0 if r < 0.5 else 1
            self.symbol_values.append(y)

    def calculate_landmarks(self):
        # TODO: set_landmarks(i, values) ? -> direkt mit check ob i auch passt -> property
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
            c += 64
            self.sequence += chr(c)