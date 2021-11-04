from Models.Interfaces.DecoderInterface import DecoderInterface
import random


class ExampleDecoder(DecoderInterface):
    def __init__(self):
        self.num_receivers = 3
        self.receiver_types = ["ExampleReceiver"] * self.num_receivers
        self.receiver_descriptions = None
        self.landmark_names = ['Test1', 'Test2']
        #self.landmark_names = None
        self.landmark_symbols = ['x', 'd']
        # self.receiver_descriptions = ["ExampleReceiver1", "ExampleReceiver2", "ExampleReceiver3"]
        # The receiver descriptions are optional
        # Landmarks are also optional
        super().__init__(self.num_receivers, self.receiver_types, receiver_descriptions=self.receiver_descriptions,
                         landmark_names=self.landmark_names, landmark_symbols=self.landmark_symbols)

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
            print(c)
            self.sequence += chr(c)