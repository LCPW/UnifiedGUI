import time

from Models.Interfaces.EncoderInterface import EncoderInterface
from Models.Implementations.Transmitters.BartelsTransmitter import BartelsTransmitter


class BartelsEncoder(EncoderInterface):

    def __init__(self, parameters, parameter_values):
        super().__init__(parameters, parameter_values)
        self.port = parameter_values['Port']
        self.bartels = BartelsTransmitter(self.port)
        self.transmitters = [self.bartels]
        self.allowed_sequence_values = [chr(i) for i in range(0, 128)]
        self.voltage = parameter_values['Voltage [V]']                          # Set micropump voltage
        self.frequency = parameter_values['Frequency [Hz]']                     # Set micropump frequency
        self.channel = parameter_values['Channel']                              # Set Channel 1-4
        self.modulation = parameter_values['Modulation']                        # 2-ASK (0,1) / 4-ASK (00,01,10,11)
        self.sleep_time = parameter_values['Sleep time [s]']                    # Waiting time until the next symbol
        self.symbolinterval = parameter_values['Symbolinterval[ms]'] / 1000     # Waiting time between the bits
        self.timezero = time.time()                                             # Start system time from 0
        self.timer = 0                                                          # Only for testing (symbol  number)
        self.nextsymbol = 0                                                     # Set slots for sending
        super().setup()

    def encode(self, sequence):

        symbol_values = []                                                      # Create list for symbols
        ask4list = []                                                           # Create list for 4-ASK
        numascii = [ord(i) for i in sequence]                                   # Change sequence in Unicode
        binarylist = [format(i, "08b") for i in numascii]                       # Change Unicode in Bitsequence

        for x in range(len(binarylist)):                                        # Change Bitsequence in single Bits
            binaryindex = [int(a) for a in str(binarylist[x])]
            for i in range(len(binaryindex)):

                if self.modulation == "2-ASK":                                  # Add single Bit to symbol list
                    if i % 8 == 0:
                        continue
                    symbol_values.append(str(binaryindex[i]))

                if self.modulation == "4-ASK":                                  # Add two Bits to symbol list
                    ask4list.append(str(binaryindex[i]))
                    if i % 2 == 1:
                        symbol_values.append(str((ask4list[i - 1]) + (ask4list[i])))

            ask4list.clear()
            symbol_values.append("-")

        self.timezero = time.time()                                             # Restart system time
        self.nextsymbol = 0                                                     # Restart slots for sending
        return symbol_values

    def parameters_edited(self):

        self.channel = self.parameter_values['Channel']
        self.frequency = self.parameter_values['Frequency [Hz]']
        self.voltage = self.parameter_values['Voltage [V]']
        self.sleep_time = self.parameter_values['Sleep time [s]']
        self.port = self.parameter_values['Port']
        self.modulation = self.parameter_values['Modulation']
        self.symbolinterval = self.parameter_values['Symbolinterval[ms]'] / 1000

    def transmit_single_symbol_value(self, symbol_value):
        while (time.time() - self.timezero) < self.nextsymbol:                  # ... system time waits until nextsymbol
            pass

        # MANUALLY #                                                            # only for testing
        if self.modulation == "manually":
            self.bartels.micropump(self.channel, self.voltage, self.frequency)  # set voltage and frequency of micropump

        # 2-ASK #
        if symbol_value != " -":                                                # If the Symbol 0 or 1 then ...

            if self.modulation == "2-ASK":
                print(str(self.timer) + ". gesendet: " + str(symbol_value) + "  " + str(time.time() - self.timezero))
                # print system time + Symbol / only for testing
                self.bartels.micropump(self.channel, int(symbol_value) * self.voltage, self.frequency)
                self.nextsymbol = round(self.nextsymbol + self.symbolinterval, 1)  # Determine nextsymbol + interval
                self.timer = (self.timer + 1) % 7                              # Define symbol number / only for testing

            if self.modulation == "4-ASK":

                if symbol_value == " 00":
                    self.voltage = 25
                if symbol_value == " 01":
                    self.voltage = 100
                if symbol_value == " 10":
                    self.voltage = 150
                if symbol_value == " 11":
                    self.voltage = 250

                print(str(self.timer) + ". gesendet: " + str(symbol_value) + "  " + str(time.time() - self.timezero))
                self.bartels.micropump(self.channel, self.voltage, self.frequency)
                self.nextsymbol = round(self.nextsymbol + self.symbolinterval, 1)
                self.timer = (self.timer + 1) % 4

        else:  # If the Symbol "-" ...

            self.bartels.micropump(self.channel, 0, 50)

            if self.symbolinterval == 0.1:
                self.nextsymbol = round(self.nextsymbol + 1 - self.symbolinterval * 7 + self.sleep_time - 1, 0)
            else:
                self.nextsymbol = round(self.nextsymbol + self.symbolinterval + self.sleep_time - 1, 1)
            print(" \r\n")  # only for testing


def get_parameters():
    parameters = [
        {
            'description': "Port",
            'dtype': 'string',
            'default': "COM15",
            'max_length': 5,
        },

        {
            'description': "Modulation",
            'dtype': 'item',
            'default': "2-ASK",
            'items': ["manually", "2-ASK", "4-ASK"],
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
