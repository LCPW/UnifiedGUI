from Models.Interfaces.DecoderInterface import DecoderInterface


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
        self.symbol_values = ["0"] * x

    def calculate_landmarks(self):
        #x = [self.symbol_intervals[a] + 0.5 * (self.symbol_intervals[a+1] - self.symbol_values[a]) for a in range(len(self.symbol_intervals))]
        x = self.symbol_intervals
        #y = [self.received[0][0, i] for i in x]
        y = [0.5] * len(self.symbol_intervals)
        for i in range(self.num_landmarks):
            self.landmarks[i] = {'x': x, 'y': [a + i for a in y]}