"""
Author: Max Bartunik
E-mail: max.bartunik@fau.de
"""


from Utils import Logging
import time
import serial
import serial.tools.list_ports
import graycode
import math

from Models.Interfaces.EncoderInterface import EncoderInterface
from Models.Implementations.Transmitters.IsmatecTransmitter import IsmatecTransmitter

class IsmatecEncoder(EncoderInterface):
    def __init__(self, parameters, parameter_values):
        super().__init__(parameters, parameter_values)

        # update settings
        self.parameters_edited()
        super().setup()

    def bits_from_string(sequence):

        sequence_in_bytes = [ord(i) for i in sequence]
        binary_sequence = [(byte >> i) & 1 for i in reversed(range(8)) for byte in sequence_in_bytes]

        return binary_sequence


    def encode(self, sequence):
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

        is_binary_input = all(val == "1" or val == "0" for val in sequence)

        binary_sequence = []
        if is_binary_input:
            binary_sequence = [int(val) for val in sequence]
        else:
            binary_sequence = IsmatecEncoder.bits_from_string(sequence)


        modulation_index = int(self.modulation_index)
        bit_per_symbol = math.log(modulation_index, 2)

        symbol_count = math.floor(len(binary_sequence)/bit_per_symbol)
        symbol_values = []
        for symbol_index in range(symbol_count):
            symbol_binary = int("0", bit_per_symbol)
            for b in range(bit_per_symbol):
                symbol_binary |= binary_sequence[symbol_index + b] << bit_per_symbol-b
            
            symbol_values.append(graycode.gray_code_to_tc(symbol_binary))

        return symbol_values

    # update parameters
    def parameters_edited(self):
        """
        Update parameters
        - check parameters during running time
        - update parameters during running time
        - limit injection duration (symbol interval - 25ms)
        - limit modulation index to 8
        """
        self.background_channel = self.parameter_values['background flow channel']
        self.injection_channel = self.parameter_values['injection flow channel']
        self.background_rate = self.parameter_values['background flow rate [RPM]']
        self.injection_rate = self.parameter_values['injection flow rate [RPM]']

        self.port = self.parameter_values['port']

        self.modulation = self.parameter_values['modulation']
        self.modulation_index = self.parameter_values['modulation index']

        self.symbol_interval = self.parameter_values["symbol interval (CSK) [ms]"]
        self.base_time = self.parameter_values["base time (PSK/TSK) [ms]"]
        self.extra_time = self.parameter_values["extra time per symbol (PSK/TSK) [ms]"]
        self.injection_duration = self.parameter_values["injection duration (per value for CSK) [ms]"]

        self.allowed_symbol_values = range(0, int(self.modulation_index))

        if self.modulation == "CSK" and self.injection_duration*int(self.modulation_index) > self.symbol_interval:
            Logging.warn("Nonsensical configuration: Max. injection duration is longer than symbol interval.")
        
        psk_total_length = self.base_time + int(self.modulation_index)*self.extra_time
        if self.modulation == "PSK" and self.injection_duration > psk_total_length:
            Logging.warn("Nonsensical configuration: Injection duration is longer than symbol interval.")
        
        if self.modulation == "TSK" and self.injection_duration > self.base_time:
            Logging.warn("Nonsensical configuration: Injection duration is longer than TSK minimal duration.")

        if self.modulation == "CSK":
            #CSK uses fixed symbol interval
            self.sleep_time = self.symbol_interval
        #TSK and PSK symbol interval has to be calculated ad-hoc, as value dependant

        #Clean up
        for tx in self.transmitters:
            try:
                tx.shutdown()
            except:
                pass
        
        
        ismatec = IsmatecTransmitter(self.port)
        ismatec.pump_set_constant_rate(self.background_channel, self.background_rate)
        ismatec.pump_set_time_rate(self.injection_channel, self.injection_duration)
        #For TSK and PSK set fixed pulse injection
        ismatec.pump_set_time_duration(self.injection_channel, self.injection_duration)
        self.transmitters = [ismatec]


    def prepare_transmission(self, symbol_values):
        if self.modulation == "TSK":
            #We have to calculate injection delay sequence for TSK
            delay_set = [self.base_time + self.extra_time*value for value in symbol_values[1:]]
            #end
            delay_set.append(self.base_time + self.extra_time*self.modulation_index)
            self.sleep_time = delay_set

        elif self.modulation == "PSK":
            #We have to calculate injection delay sequence for PSK
            psk_interval = self.base_time + int(self.modulation_index)*self.extra_time
            delay_set = []
            for i in range(1, len(symbol_values)):
                this_value_time = self.base_time + symbol_values[i]*self.extra_time
                last_value_wait = psk_interval - (self.base_time + symbol_values[i-1]*self.extra_time)
                delay_set.append(last_value_wait+this_value_time)

            #end
            delay_set.append(self.base_time + self.extra_time*self.modulation_index)

            self.sleep_time = delay_set

        #start background flow
        for tx in self.transmitters:
            tx.pump_start(self.background_channel)

    def clean_up_transmission(self):
        #Stop background flow once we are done
        #TODO: Perhaps introduce a static wait time
        for tx in self.transmitters:
            tx.pump_stop(self.background_channel)

    def transmit_single_symbol_value(self, symbol_value):
        """
        Transmit data
        - check modulation index and transmit accordingly
        - This will be called with correct timing
        """
        symbol_value = str(symbol_value).strip()

        for tx in self.transmitters:
            #For TSK and PSK injection burst is fixed - go ahead
            if self.modulation == "CSK":
                #Injection burst length depends on symbol value
                injection_duration = symbol_value*self.injection_duration
                tx.pump_set_time_duration(self.injection_channel, injection_duration)
            
            tx.pump_start(self.injection_channel)


    def available_ports():
        ports = serial.tools.list_ports.comports()
    
        suggested_port = ""
        for port in sorted(ports):
            # TODO find Reglo ICC port
            pass
            
        return ports, suggested_port

    def get_parameters():
        """
        Parameter setting
        - limit parameters
        - set default values
        """

        ports, suggested_port = IsmatecEncoder.available_ports()

        parameters = [
            {
                'description': "port",
                'dtype': 'item',
                'default': suggested_port,
                'items': [port.name for port in ports],
            },

            {
                'description': "background flow channel",
                'dtype': 'item',
                'default': "3",
                'items': ["1", "2", "3", "4"],
            },

            {
                'description': "background flow rate [RPM]",
                'dtype': 'float',
                'decimals': 2,
                'default': 83,
                'min': 0.1,
                'max': 100,
            },

            {
                'description': "injection flow channel",
                'dtype': 'item',
                'default': "4",
                'items': ["1", "2", "3", "4"],
            },

            {
                'description': "injection flow rate [RPM]",
                'dtype': 'float',
                'decimals': 2,
                'default': 83,
                'min': 0.1,
                'max': 100,
            },

            {
                'description': "modulation",
                'dtype': 'item',
                'default': "CSK",
                'items': ["CSK", "PSK", "TSK"],
            },

            {
                'description': "modulation index",
                'dtype': 'item',
                'default': "2",
                'items': ["2", "4", "8", "16", "32", "64", "128", "256", "512", "1024"]
            },

            {
                'description': "symbol interval (CSK) [ms]",
                'decimals': 0,
                'dtype': 'float',
                'min': 100,
                'max': 10000,
                'default': 500,
            },
                    {
                'description': "base time (PSK/TSK) [ms]",
                'dtype': 'int',
                'decimals': 0,
                'min': 100,
                'max': 10000,
                'default': 500,
            },

            {
                'description': "extra time per symbol (PSK/TSK) [ms]",
                'dtype': 'int',
                'decimals': 0,
                'min': 1,
                'max': 10000,
                'default': 10,
            },

            {
                'description': "injection duration (per value for CSK) [ms]",
                'dtype': 'int',
                'decimals': 0,
                'min': 100,
                'max': 10000,
                'default': 100
            }
        ]
        return parameters


    def individual_encode(sequence, symbol_values):
        """
        Individual encoding
        - #on = micropump on (reference: voltage and frequency)
        - #off =  micropump off
        - #i + number = place "1" according to the number
        - #a + data =  separate data and place "," after each symbol
        """
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
