import time

from Models.Interfaces.EncoderInterface import EncoderInterface
from Models.Implementations.Transmitters.BartelsTransmitter import BartelsTransmitter


class BartelsEncoder(EncoderInterface):

    def __init__(self, parameters, parameter_values):
        super().__init__(parameters, parameter_values)
        self.port = parameter_values['Port']
        self.bartels = BartelsTransmitter(self.port)
        self.transmitters = [BartelsTransmitter(self.port)]
        self.allowed_sequence_values = [chr(i) for i in range(0, 128)]
        self.voltage = parameter_values['Voltage [V]']
        self.frequency = parameter_values['Frequency [Hz]']
        self.channel = parameter_values['Channel']
        self.mode = parameter_values['Mode']
        self.modulation = parameter_values['Modulation']
        self.sleep_time = parameter_values['Sleep time [s]']

        super().setup()

    def encode(self, sequence):
        symbol_values = []

        numascii = [ord(i) for i in sequence]
        asciilist = [str.encode(str(i)).decode("ascii") for i in numascii]
        binarylist = [format(i, "07b") for i in numascii]

        sequence = sequence.replace(",", " ")
        sequence = sequence.replace(";", " ")
        wordlist = sequence.split()

        if self.mode == "word":
            for i in range(len(wordlist)):
                symbol_values.append(str(wordlist[i]))
            symbol_values.append("-1")
            return symbol_values

        elif self.mode == "ascii":
            for i in range(len(asciilist)):
                symbol_values.append(str(asciilist[i]))
            symbol_values.append("-")
            return symbol_values

        elif self.mode == "binary":
            for x in range(len(binarylist)):
                binaryindex = [int(a) for a in str(binarylist[x])]
                for i in range(len(binaryindex)):
                    symbol_values.append(str(binaryindex[i]))
                symbol_values.append("-")
            return symbol_values

    def parameters_edited(self):

        self.mode = self.parameter_values['Mode']
        self.channel = self.parameter_values['Channel']
        self.frequency = self.parameter_values['Frequency [Hz]']
        self.voltage = self.parameter_values['Voltage [V]']
        self.sleep_time = self.parameter_values['Sleep time [s]']
        self.port = self.parameter_values['Port']
        self.modulation = self.parameter_values['Modulation']

    def transmit_single_symbol_value(self, symbol_value):

        ################## MANUALLY ######################
        if self.modulation == "manually":
            self.bartels.smp.write(
                b"P" + str.encode(str(self.channel)) + b"V" + str.encode(str(self.voltage)) + b"\r\n")
            print(self.bartels.smp.readline().decode("ascii"))
            self.bartels.smp.write(b"F" + str.encode(str(self.frequency)) + b"\r\n")
            print(self.bartels.smp.readline().decode("ascii"))

        ############### AUTOMATICALLY 2-ASK ####################
        elif self.modulation == "2-ASK":

            if symbol_value != " -":
                self.transmitters[0].value = int(symbol_value)
                self.bartels.smp.write(b"P" + str.encode(str(self.channel)) +
                                       b"V" + str.encode(str(int(symbol_value) * self.voltage)) +
                                       b"b\r\n")
                self.bartels.smp.readline().decode("ascii")
            else:
                self.bartels.smp.write(b"P" + str.encode(str(self.channel)) +
                                       b"V0" + # str.encode(str(int(symbol_value) * self.voltage)) +
                                       b"b\r\n")
                self.bartels.smp.readline().decode("ascii")
                time.sleep(0.1)


def get_parameters():
    parameters = [
        {
            'description': "Mode",
            'dtype': 'item',
            'default': "binary",
            'items': ["ascii", "word", "binary"],
        },

        {
            'description': "Modulation",
            'dtype': 'item',
            'default': "4-ASK",
            'items': ["manually", "2-ASK", "4-ASK"],
        },

        {
            'description': "Port",
            'dtype': 'string',
            'default': "COM",
            'max_length': 5,
        },

        {
            'description': "Channel",
            'dtype': 'item',
            'default': "4",
            'items': ["1", "2", "3", "4"],
        },

        {
            'description': "Voltage [V]",
            'dtype': 'int',
            'decimals': 0,
            'default': 25,
            'min': 0,
            'max': 250,
        },

        {
            'description': "Frequency [Hz]",
            'dtype': 'int',
            'decimals': 0,
            'default': 0,
            'min': 0,
            'max': 850,
        },

        {
            'description': "Sleep time [s]",
            'decimals': 3,
            'dtype': 'float',
            'min': 0,
            'max': 100,
            'default': 0.0,
        }
    ]
    return parameters
