"""
Author: Steve Kungu
E-mail: steve.kungu@fau.de
"""


import time

from Models.Interfaces.EncoderInterface import EncoderInterface
from Models.Implementations.Transmitters.BartelsTransmitter import BartelsTransmitter, micropump_find_ports


class BartelsEncoder(EncoderInterface):

    def __init__(self, parameters, parameter_values):
        super().__init__(parameters, parameter_values)
        self.port = parameter_values['port']
        self.bartels = BartelsTransmitter(self.port)                                # get port from PC
        self.transmitters = [self.bartels]                                          # set port
        self.voltage = parameter_values['voltage [V]']                              # set micropump voltage
        self.frequency = parameter_values['frequency [Hz]']                         # set micropump frequency
        self.channel = parameter_values['channel']                                  # set channel
        self.modulation_index = self.parameter_values['modulation index']           # set modulation index
        self.modulation = parameter_values['modulation']                            # set modulation CSK, TSK, PSK
        self.injection_duration = parameter_values['injection duration [ms]']       # set injection duration
        self.symbol_interval = parameter_values['symbol interval [ms]']             # set waiting time between Symbols
        self.startTime = time.time()                                                # get current system time
        self.base_time = self.parameter_values['base time (b) [ms]']                # set slots for sending
        self.extra_time = self.parameter_values['extra time per symbol (e) [ms]']   # set extra time (TSK)
        self.next_interval = 0                                                      # set for injection duration
        self.parameters_edited()                                                    # update settings
        super().setup()

        """
           
        Initialization of the micropump

        - set right port
        - set start parameters
        - update set parameters
        - determine current runtime
        """

    def encode(self, sequence):

        symbol_values = []                                                  # create list for symbols
        list4csk = []                                                       # create list for 4-CSK
        list8csk = []                                                       # create list for 8-CSK
        sequence_in_decimal = [ord(i) for i in sequence]                    # change sequence in decimal (ascii)
        decimal_in_8bit = [format(i, "08b") for i in sequence_in_decimal]   # change decimal in 8bit sequence

        for x in range(len(decimal_in_8bit)):
            binary8index = [int(a) for a in str(decimal_in_8bit[x])]        # change 8bit sequence in single Bits

            for i in range(len(binary8index)):
                if self.modulation_index == "2":                            # 1Bit --> 1Symbol
                    if i % 8 == 0:
                        continue
                    symbol_values.append(str(binary8index[i]))

                elif self.modulation_index == "4":                          # 2Bit --> 1Symbol
                    list4csk.append(str(binary8index[i]))
                    if i % 2 == 1:
                        symbol_values.append(str((list4csk[i - 1]) + (list4csk[i])))

                elif self.modulation_index == "8":                          # 3Bit --> 1Symbol
                    list8csk.append(str(binary8index[i]))
                    if i % 3 == 1 and i > 1:
                        symbol_values.append(str((list8csk[i - 2]) + (list8csk[i - 1]) + (list8csk[i])))

            if self.modulation == "TSK" or self.modulation == "PSK":
                symbol_values.clear()
                symbol_values.append(sequence)

            list4csk.clear()
            list8csk.clear()
            # symbol_values.append("-")                                     # set "-" after each Symbol
        if sequence == "":
            symbol_values = 0

        symbol_values.append("-")

        if sequence[0] == "#":                                              # "#" for individual codes
            symbol_values.clear()
            symbol_values = individual_encode(sequence, symbol_values)      # individual codes (see function)

        self.next_interval = 1                                              # restart slots for sending
        self.bartels.micropump_set_frequency(self.frequency)                # set frequency
        self.startTime = time.time()                                        # update start time
        return symbol_values

    """

    Coding of the information
    
    - encoding depending on modulation and modulation index
    - convert letters to numbers (CSK)
        - convert numbers to binary system 
    - no conversion (PSK, TSK)
    - set first injection time (at 1 sec)
    - set frequency
    - update start time to current runtime
    - encoding individual codes
    """

    def parameters_edited(self):                                            # update parameters
        self.channel = self.parameter_values['channel']
        self.frequency = self.parameter_values['frequency [Hz]']
        self.voltage = self.parameter_values['voltage [V]']
        self.port = self.parameter_values['port']
        self.modulation = self.parameter_values['modulation']
        self.symbol_interval = self.parameter_values['symbol interval [ms]']
        self.injection_duration = self.parameter_values['injection duration [ms]']
        self.base_time = self.parameter_values['base time (b) [ms]']
        self.extra_time = self.parameter_values['extra time per symbol (e) [ms]']
        self.modulation_index = self.parameter_values['modulation index']

        if self.injection_duration + 25 >= self.symbol_interval:     # limit injection duration to symbol interval -25ms
            self.injection_duration = self.symbol_interval - 25
            self.parameter_values['injection duration [ms]'] = self.injection_duration
        if self.modulation == "CSK" and int(self.modulation_index) > 8:  # limit modulation index to 8 for CSK
            self.parameter_values['modulation index'] = "8"
            self.modulation_index = "8"

        """
        
        Update parameters   
          
        - check parameters during running time
        - update parameters during running time
        - limit injection duration (symbol interval - 25ms)
        - limit modulation index to 8
        """

    def transmit_single_symbol_value(self, symbol_value):

        symbol_value = str(symbol_value).strip()

        if not symbol_value == "-":

            if symbol_value == "on" or symbol_value == "off":
                self.bartels.onoff(self.channel, self.voltage, self.frequency, symbol_value)

            elif self.modulation == "CSK":
                if self.modulation_index == "2":
                    while (time.time() - self.startTime) < self.next_interval:  # wait until next injection time
                        pass
                    self.bartels.micropump_set_voltage_duration(self.channel, int(symbol_value) * self.voltage,
                                                                int(symbol_value) * self.injection_duration)

                elif self.modulation_index == "4":
                    if self.symbol_interval < 250:      # limit symbol intervall to >= 250
                        self.symbol_interval = 250
                        self.parameter_values['symbol interval [ms]'] = 250
                    self.bartels.modulation_4CSK(self.channel, symbol_value, self.startTime, self.next_interval)

                elif self.modulation_index == "8":
                    if self.symbol_interval < 500:      # limit symbol intervall to >= 500
                        self.symbol_interval = 500
                        self.parameter_values['symbol interval [ms]'] = 500
                    self.bartels.modulation_8CSK(self.channel, symbol_value, self.startTime, self.next_interval)

                self.next_interval = round(self.next_interval + self.symbol_interval / 1000, 3)

            elif self.modulation == "TSK":
                self.bartels.modulation_TSK(self.channel, symbol_value, self.startTime, self.next_interval,
                                            self.voltage, self.injection_duration)
                next_timeslot = self.base_time/1000 + int(symbol_value) * self.extra_time/1000
                self.next_interval = round(self.next_interval + next_timeslot, 3)

            elif self.modulation == "PSK":
                self.bartels.modulation_PSK(self.channel, symbol_value, self.startTime, self.next_interval,
                                            self.extra_time / 1000, self.voltage, self.injection_duration)
                next_timeslot = round(self.base_time/1000 + (int(self.modulation_index)-1) * self.extra_time/1000, 3)
                self.next_interval = round(self.next_interval + next_timeslot, 3)

        else:  # symbol = "-"
            self.bartels.micropump_set_voltage_duration(self.channel, 0, 0)
            if self.modulation == "CSK":
                self.next_interval = round(self.next_interval + self.symbol_interval / 1000, 3)

        """
        
        Transmit data
         
        - check modulation index and transmit accordingly
        - set injection times
        """


def get_parameters():
    parameters = [
        {
            'description': "port",
            'dtype': 'string',
            'default': micropump_find_ports(),
            'max_length': 5,
        },

        {
            'description': "channel",
            'dtype': 'item',
            'default': "1",
            'items': ["1", "2", "3", "4"],
        },

        {
            'description': "modulation index",
            'dtype': 'item',
            'default': "2",
            'items': ["2", "4", "8", "16", "32", "64", "128", "256", "512", "1024"]
        },

        {
            'description': "modulation",
            'dtype': 'item',
            'default': "CSK",
            'items': ["CSK", "PSK", "TSK"],
        },

        {
            'description': "voltage [V]",
            'dtype': 'int',
            'decimals': 0,
            'default': 250,
            'min': 0,
            'max': 250,
        },

        {
            'description': "frequency [Hz]",
            'dtype': 'int',
            'decimals': 0,
            'default': 70,
            'min': 50,
            'max': 800,
        },

        {
            'description': "symbol interval [ms]",
            'decimals': 0,
            'dtype': 'float',
            'min': 25,
            'max': 10000,
            'default': 500,
        },

        {
            'description': "injection duration [ms]",
            'dtype': 'int',
            'decimals': 0,
            'min': 10,
            'max': 10000,
            'default': 100
        },

        {
            'description': "base time (b) [ms]",
            'dtype': 'int',
            'decimals': 0,
            'min': 1,
            'max': 10000,
            'default': 500,
        },

        {
            'description': "extra time per symbol (e) [ms]",
            'dtype': 'int',
            'decimals': 0,
            'min': 1,
            'max': 10000,
            'default': 10,
        },
    ]
    return parameters


"""

Parameter setting

- limit parameters
- set default values
"""


def individual_encode(sequence, symbol_values):
    if sequence[1] == "i":
        for i in range(int(sequence[2:])):
            symbol_values.append(1)
            i += 1
        symbol_values.append("-")
    if sequence[1] == "a":
        for i in range(2, len(sequence)):
            symbol_values.append(sequence[i])
        symbol_values.append("-")
    if sequence[1:] == "on" or sequence[1:] == "ON":
        symbol_values.append("on")
    if sequence[1:] == "off" or sequence[1:] == "OFF":
        symbol_values.append("off")
    return symbol_values


"""

Individual encoding

- #on = micropump on (reference: voltage and frequency)
- #off =  micropump off
- #i + number = place "1" according to the number
- #a + data =  separate data and place "," after each symbol
"""
