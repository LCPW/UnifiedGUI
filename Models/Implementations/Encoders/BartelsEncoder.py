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
        #self.translation = parameter_values['Translation']
        self.modulation = parameter_values['Modulation']
        self.sleep_time = parameter_values['Sleep time [s]']
        self.symbolinterval = parameter_values['Symbolinterval[ms]']/1000
        self.timersymbol = 0
        self.timer = 0
        self.nextsymbol = 0.1
        self.timestart = 10
        self.timezero = time.time()
        self.korrektur = 0
        self.symbolint = 0
        super().setup()

    def encode(self, sequence):
        symbol_values = []

        numascii = [ord(i) for i in sequence]

        # if self.translation == "word":
        #
        #     sequence = sequence.replace(",", " ")
        #     sequence = sequence.replace(";", " ")
        #     wordlist = sequence.split()
        #
        #     for i in range(len(wordlist)):
        #         symbol_values.append(str(wordlist[i]))
        #     symbol_values.append("-1")
        #     return symbol_values
        #
        # if self.translation == "ascii":
        #
        #     asciilist = [str.encode(str(i)).decode("ascii") for i in numascii]
        #
        #     for i in range(len(asciilist)):
        #         symbol_values.append(str(asciilist[i]))
        #     symbol_values.append("-")
        #     return symbol_values

        if self.modulation == "2-ASK":

            binarylist = [format(i, "07b") for i in numascii]

            for x in range(len(binarylist)):
                binaryindex = [int(a) for a in str(binarylist[x])]
                for i in range(len(binaryindex)):
                    symbol_values.append(str(binaryindex[i]))
                symbol_values.append("-")
            self.timezero = time.time()
            self.nextsymbol = 0
            return symbol_values

        if self.modulation == "4-ASK":

            binarylist = [format(i, "08b") for i in numascii]
            ask4list = []

            for x in range(len(binarylist)):
                binaryindex = [int(a) for a in str(binarylist[x])]
                for i in range(len(binaryindex)):
                    ask4list.append(str(binaryindex[i]))
                    if i % 2 == 1:
                        symbol_values.append(str((ask4list[i - 1]) + (ask4list[i])))
                ask4list.clear()
                symbol_values.append("-")
                self.timezero = time.time()
                self.nextsymbol = 0
            return symbol_values

    def parameters_edited(self):

        #self.translation = self.parameter_values['Translation']
        self.channel = self.parameter_values['Channel']
        self.frequency = self.parameter_values['Frequency [Hz]']
        self.voltage = self.parameter_values['Voltage [V]']
        self.sleep_time = self.parameter_values['Sleep time [s]']
        self.port = self.parameter_values['Port']
        self.modulation = self.parameter_values['Modulation']
        self.symbolinterval = self.parameter_values['Symbolinterval[ms]']/1000

    def transmit_single_symbol_value(self, symbol_value):
        #start = str(time.time() - self.timezero)

        ################## MANUALLY ######################
        if self.modulation == "manually":
            self.bartels.smp.write(
                b"P" + str.encode(str(self.channel)) + b"V" + str.encode(str(self.voltage)) + b"\r\n")
            print(self.bartels.smp.readline().decode("ascii"))
            self.bartels.smp.write(b"F" + str.encode(str(self.frequency)) + b"\r\n")
            print(self.bartels.smp.readline().decode("ascii"))

        ############### AUTOMATICALLY 2-ASK ####################
        if self.modulation == "2-ASK":

            if symbol_value != " -":
                while (time.time()-self.timezero) < self.nextsymbol:
                    ""

                print(str(self.timer) + ". gesendet: " + str(symbol_value) + "  " + str(time.time() - self.timezero))
                self.bartels.smp.write(b"P" + str.encode(str(self.channel)) +
                                       b"V" + str.encode(str(int(symbol_value) * self.voltage)) +
                                       b"\r\n")
                self.bartels.smp.readline().decode("ascii")
                self.bartels.smp.write(b"F" + str.encode(str(self.frequency)) + b"\r\n")
                self.bartels.smp.readline().decode("ascii")

                #self.transmitters[0].value = int(symbol_value)
                self.nextsymbol = round(self.nextsymbol + self.symbolinterval, 2)
                self.timer = (self.timer + 1) % 7

            else:

                while (time.time() - self.timezero) <= (self.nextsymbol):
                    ""

                print("-. ges: " + str(symbol_value) + " " + str(time.time() - self.timezero) + " " + str(self.nextsymbol))
                self.bartels.smp.write(b"P" + str.encode(str(self.channel)) + b"V0b\r\n")
                self.bartels.smp.readline().decode("ascii")
                self.bartels.smp.write(b"F0\r\n")
                self.bartels.smp.readline().decode("ascii")
                self.nextsymbol = round(self.nextsymbol + self.symbolinterval + self.sleep_time-1, 2) #1-ssy*7 bei 100ms
                print(" \r\n")

        ############### AUTOMATICALLY 4-ASK ####################
        if self.modulation == "4-ASK":

            if symbol_value != " -":
                self.transmitters[0].value = int(symbol_value)

                if symbol_value == " 00":
                    self.voltage = 25
                if symbol_value == " 01":
                    self.voltage = 100
                if symbol_value == " 10":
                    self.voltage = 150
                if symbol_value == " 11":
                    self.voltage = 250

                while (time.time() - self.timezero) <= (self.nextsymbol):
                    ""

                print(str(self.timer) + ". gesendet: " + str(symbol_value) + "  " + str(time.time() - self.timezero))
                self.bartels.smp.write(b"P"+str.encode(str(self.channel))+b"V"+str.encode(str(self.voltage))+b"\r\n")
                self.bartels.smp.readline().decode("ascii")
                self.nextsymbol = round(self.nextsymbol + self.symbolinterval, 2)
                self.bartels.smp.write(b"F" + str.encode(str(self.frequency)) + b"\r\n")
                self.bartels.smp.readline().decode("ascii")
                self.timer = (self.timer + 1) % 4

            else:

                while (time.time() - self.timezero) <= (self.nextsymbol):
                    ""

                print("-. gesendet: " + str(symbol_value) + "  " + str(time.time() - self.timezero))
                self.bartels.smp.write(b"P" + str.encode(str(self.channel)) + b"V0b\r\n")
                self.bartels.smp.readline().decode("ascii")
                self.bartels.smp.write(b"F50\r\n")
                self.bartels.smp.readline().decode("ascii")
                self.nextsymbol = round(self.nextsymbol + self.symbolinterval, 2)
                print(" \r\n")


        #self.korrektur = time.time() - self.timezero - float(start)
        #print(str(self.korrektur))


def get_parameters():
    parameters = [
        # {
        #     'description': "Translation",
        #     'dtype': 'item',
        #     'default': "binary",
        #     'items': ["ascii", "word", "binary"],
        # },

        {
            'description': "Modulation",
            'dtype': 'item',
            'default': "2-ASK",
            'items': ["manually", "2-ASK", "4-ASK"],
        },

        {
            'description': "Port",
            'dtype': 'string',
            'default': "COM5",
            'max_length': 5,
        },

        {
            'description': "Channel",
            'dtype': 'item',
            'default': "1",
            'items': ["1", "2", "3", "4"],
        },

        {
            'description': "Voltage [V]",
            'dtype': 'int',
            'decimals': 0,
            'default': 250,
            'min': 0,
            'max': 250,
        },

        {
            'description': "Frequency [Hz]",
            'dtype': 'int',
            'decimals': 0,
            'default': 70,
            'min': 50,
            'max': 850,
        },

        {
            'description': "Sleep time [s]",
            'decimals': 1,
            'dtype': 'float',
            'min': 1,
            'max': 100,
            'default': 1,
        },

        {
            'description': "Symbolinterval[ms]",
            'decimals': 0,
            'dtype': 'float',
            'min': 100,
            'max': 1000,
            'default': 100,
        }


    ]
    return parameters
