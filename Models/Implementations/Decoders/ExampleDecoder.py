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
    def __init__(self, parameter_values):
        super().__init__(parameter_values)
        # Mandatory
        self.receiver_types = ["ExampleReceiver"] * 3

        # Optional
        self.landmark_names = ['Test1', 'Test2']
        # self.landmark_symbols = ['x', 'd']

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
        #print(len(self.symbol_values))
        #print(len(self.symbol_intervals))

    def calculate_landmarks(self):
        # TODO: set_landmarks(i, values) ? -> direkt mit check ob i auch passt
        #x = [self.symbol_intervals[a] + 0.5 * (self.symbol_intervals[a+1] - self.symbol_values[a]) for a in range(len(self.symbol_intervals))]
        x = self.symbol_intervals
        #y = [self.received[0][0, i] for i in x]
        y = [0.5] * len(self.symbol_intervals)
        for i in range(self.num_landmarks):
            self.landmarks[i] = {'x': x, 'y': [a + i for a in y]}

    def calculate_sequence(self):
        # TODO: Cringe
        self.sequence = ""
        l = len(self.symbol_values) - 4
        length = l if l > 0 else 0
        for i in range(length)[::4]:
            v1, v2, v3, v4 = self.symbol_values[i], self.symbol_values[i+1], self.symbol_values[i+2], self.symbol_values[i+3]
            c = v1 + v2 + v3 + v4 + 64
            #print(c)
            self.sequence += chr(c)