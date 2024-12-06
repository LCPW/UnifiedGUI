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
        self.transmitter_names = ["Bartels"]

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
        max_value = self.modulation_index-1

        symbol_count = math.floor(len(binary_sequence)/bit_per_symbol)

        #Prepend transmission with sync
        symbol_values = [max_value, 0, 0]
        for symbol_index in range(symbol_count):
            symbol_binary = 0
            for b in range(bit_per_symbol):
                symbol_binary |= binary_sequence[symbol_index*bit_per_symbol + b] << bit_per_symbol-b-1
            
            symbol_values.append(graycode.gray_code_to_tc(symbol_binary))

        return symbol_values

    def get_transmitter_current_symbols(self):
        """
        Returns a list of currently transmitted symbols by the transmitters. (for example: active/inactive=1/0)
        :return: A list of symbols, with a length equal to the amount of transmitters present.
        """
        transmitter_active_list = []
        for tx_idx in range(len(self.transmitters)):
            active_list = []
            channel_active = self.transmitters[tx_idx].get_channel_active()
            if self.channel1:
                active_list.append(channel_active[0])
            if self.channel2:
                active_list.append(channel_active[1])
            if self.channel3:
                active_list.append(channel_active[2])
            if self.channel4:
                active_list.append(channel_active[3])

            transmitter_active_list.append(active_list)

        return transmitter_active_list

    # update parameters
    def parameters_edited(self):
        """
        Update parameters
        - check parameters during running time
        - update parameters during running time
        - limit injection duration (symbol interval - 25ms)
        - limit modulation index to 8
        """
        self.channel1 = self.parameter_values['channel 1']
        self.channel2 = self.parameter_values['channel 2']
        self.channel3 = self.parameter_values['channel 3']
        self.channel4 = self.parameter_values['channel 4']
        self.frequency = self.parameter_values['frequency [Hz]']
        self.voltage = self.parameter_values['voltage [V]']
        self.port = self.parameter_values['port']
        self.modulation = self.parameter_values['modulation']
        self.symbol_interval = self.parameter_values['symbol interval [ms]']
        self.injection_duration = self.parameter_values['injection duration [ms]']
        self.base_time = self.parameter_values['base time (b) [ms]']
        self.extra_time = self.parameter_values['extra time per symbol (e) [ms]']
        self.modulation_index = int(self.parameter_values['modulation index'])

        self.active_channels = int(self.channel1) + int(self.channel2) + int(self.channel3) + int(self.channel4)
        self.plot_settings = {
            'additional_datalines_active': [True, self.active_channels>1, self.active_channels>2, self.active_channels>3],
            'additional_datalines_width': 3,
            'datalines_active': [[True, self.active_channels>1, self.active_channels>2, self.active_channels>3]],
            'datalines_width': 3
        }

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
            psk_interval = self.base_time + (self.modulation_index-1)*self.extra_time
            delay_set = []
            for i in range(1, len(symbol_values)):
                this_value_time = self.base_time + symbol_values[i]*self.extra_time
                last_value_wait = psk_interval - (self.base_time + symbol_values[i-1]*self.extra_time)
                delay_set.append(last_value_wait+this_value_time)

            self.sleep_time = delay_set

        #Start pump
        for tx in self.transmitters:
            tx.micropump_set_state(True)

    def clean_up_transmission(self):
        #Stop pump
        for tx in self.transmitters:
            tx.micropump_set_state(False)
        pass

    def transmit_single_symbol_value(self, symbol_value):
        """
        Transmit data
        - check modulation index and transmit accordingly
        - This will be called with correct timing
        """

        injection_duration = self.injection_duration  # the amount of activation time (0-10000)
        #For TSK and PSK injection burst is fixed - go ahead
     
        if self.modulation == "CSK":
            #Injection burst length depends on symbol value
            injection_duration = symbol_value*self.injection_duration

        if injection_duration < 1:
            return

        for tx in self.transmitters:
            tx.micropump_set_voltage(self.channel1, self.channel2, self.channel3, self.channel4, self.voltage)

            time.sleep(injection_duration / 1000)

            tx.micropump_disable_voltages()

    def available_ports():
        ports = serial.tools.list_ports.comports()
    
        suggested_port = ports[0].name
        for port in sorted(ports):
            if BartelsTransmitter.HARDWARE_ID in port.hwid:
                conn = None            
                try:
                    conn = serial.Serial(port=port.name, baudrate=BartelsTransmitter.BAUDRATE, timeout=BartelsTransmitter.TIMEOUT)
                    conn.write_timeout = BartelsTransmitter.TIMEOUT
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
                'description': "channel 1",
                'dtype': 'bool',
                'default': True
            },
            {
                'description': "channel 2",
                'dtype': 'bool',
                'default': False
            },
            {
                'description': "channel 3",
                'dtype': 'bool',
                'default': False
            },
            {
                'description': "channel 4",
                'dtype': 'bool',
                'default': False
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
                'default': 1000,
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
                'default': 50,
            },

            {
                'description': "injection duration [ms]",
                'dtype': 'int',
                'decimals': 0,
                'min': 10,
                'max': 10000,
                'default': 200
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
