"""
Author: Steve Kungu | Max Bartunik
E-mail: steve.kungu@fau.de
"""


from Utils import Logging
import time
import serial
import serial.tools.list_ports
import graycode
import math
import re

from Models.Interfaces.EncoderInterface import EncoderInterface
from Models.Implementations.Transmitters.BartelsTransmitter import BartelsTransmitter

class BartelsEncoder(EncoderInterface):
    def __init__(self, parameters, parameter_values):
        """
        Initialization of the micropump
        - set right port
        - set start parameters
        - update set parameters
        - determine current runtime
        """
        super().__init__(parameters, parameter_values)

        # update settings
        self.parameters_edited()
        super().setup()

    def bits_from_string(sequence):

        sequence_in_bytes = [ord(i) for i in sequence]
        binary_sequence =  []
        for byte in sequence_in_bytes:
            for i in reversed(range(8)):
                binary_sequence.append((byte>>i) & 1)

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

        is_binary_input = re.search("^[01]*$", sequence)

        binary_sequence = []
        if is_binary_input:
            binary_sequence = [int(val) for val in sequence]
        else:
            binary_sequence = BartelsEncoder.bits_from_string(sequence)

        bit_per_symbol = int(math.log(self.modulation_index, 2))

        symbol_count = math.floor(len(binary_sequence)/bit_per_symbol)
        symbol_values = []
        for symbol_index in range(symbol_count):
            symbol_binary = 0
            for b in range(bit_per_symbol):
                symbol_binary |= binary_sequence[symbol_index*bit_per_symbol + b] << bit_per_symbol-b-1
            
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
        self.channel = self.parameter_values['channel']
        self.frequency = self.parameter_values['frequency [Hz]']
        self.voltage = self.parameter_values['voltage [V]']
        self.port = self.parameter_values['port']
        self.modulation = self.parameter_values['modulation']
        self.symbol_interval = self.parameter_values['symbol interval [ms]']
        self.injection_duration = self.parameter_values['injection duration [ms]']
        self.base_time = self.parameter_values['base time (b) [ms]']
        self.extra_time = self.parameter_values['extra time per symbol (e) [ms]']
        self.modulation_index = int(self.parameter_values['modulation index'])

        self.allowed_symbol_values = [str(val) for val in range(0, self.modulation_index)]

        if self.modulation == "CSK" and self.injection_duration*(self.modulation_index-1) > self.symbol_interval:
            Logging.warning("Nonsensical configuration: Max. injection duration is longer than symbol interval.")
        
        psk_total_length = self.base_time + (self.modulation_index-1)*self.extra_time
        if self.modulation == "PSK" and self.injection_duration > psk_total_length:
            Logging.warning("Nonsensical configuration: Injection duration is longer than symbol interval.")
        
        if self.modulation == "TSK" and self.injection_duration > self.base_time:
            Logging.warning("Nonsensical configuration: Injection duration is longer than TSK minimal duration.")

        if self.modulation == "CSK":
            #CSK uses fixed symbol interval
            self.sleep_time = self.symbol_interval
        #TSK and PSK symbol interval has to be calculated ad-hoc, as value dependant

        #Clean up
        if self.transmitters is not None:
            for tx in self.transmitters:
                try:
                    tx.shutdown()
                except:
                    pass

        bartels = BartelsTransmitter(self.port)
        bartels.micropump_set_frequency(self.frequency)
        self.transmitters = [bartels]


    def prepare_transmission(self, symbol_values):
        if self.modulation == "TSK":
            #We have to calculate injection delay sequence for TSK
            delay_set = [self.base_time + self.extra_time*value for value in symbol_values[1:]]
            self.sleep_time = delay_set

        elif self.modulation == "PSK":
            #We have to calculate injection delay sequence for PSK
            psk_interval = self.base_time + self.modulation_index*self.extra_time
            delay_set = []
            for i in range(1, len(symbol_values)):
                this_value_time = self.base_time + symbol_values[i]*self.extra_time
                last_value_wait = psk_interval - (self.base_time + symbol_values[i-1]*self.extra_time)
                delay_set.append(last_value_wait+this_value_time)

            self.sleep_time = delay_set

    def clean_up_transmission(self):
        pass

    def transmit_single_symbol_value(self, symbol_value):
        """
        Transmit data
        - check modulation index and transmit accordingly
        - This will be called with correct timing
        """

        injection_duration = self.injection_duration
        #For TSK and PSK injection burst is fixed - go ahead
     
        if self.modulation == "CSK":
            #Injection burst length depends on symbol value
            injection_duration = symbol_value*self.injection_duration

        for tx in self.transmitters:
                tx.micropump_set_voltage_duration(self.channel, self.voltage, injection_duration)


    def available_ports():
        ports = serial.tools.list_ports.comports()
    
        suggested_port = ports[0].name
        for port in sorted(ports):
            conn = None
            if BartelsTransmitter.HARDWARE_ID in port.hwid:            
                try:
                    conn = serial.Serial(port=port.name, baudrate=BartelsTransmitter.BAUDRATE, timeout=BartelsTransmitter.TIMEOUT)
                except serial.serialutil.SerialException:
                    #Port may be in use or wrong
                    continue
                
                conn.write(str.encode("ID\r\n"))
                read_id = conn.readline().decode('utf-8').replace("\r\n", "")
                conn.close()
                if read_id == BartelsTransmitter.DEVICE_ID:
                    suggested_port = port.name
                    break
            
        return ports, suggested_port

    def get_parameters():
        """
        Parameter setting
        - limit parameters
        - set default values
        """

        ports, suggested_port = BartelsEncoder.available_ports()

        parameters = [
            {
                'description': "port",
                'dtype': 'item',
                'default': suggested_port,
                'items': [port.name for port in ports],
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

            {
                'description': "injection duration [ms]",
                'dtype': 'int',
                'decimals': 0,
                'min': 10,
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
