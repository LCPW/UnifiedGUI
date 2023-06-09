"""
Author: Max Bartunik
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

class PocketLoCEncoder(EncoderInterface):
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
        - convert letters to numbers
            - convert numbers to binary system
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
            binary_sequence = PocketLoCEncoder.bits_from_string(sequence)

        bit_per_symbol = int(math.log(self.modulation_index, 2))
        max_value = self.modulation_index-1

        symbol_count = math.floor(len(binary_sequence)/bit_per_symbol)

        #Prepend transmission with flush and sync
        symbol_values = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, max_value, 0, 0, 1, 2, 3, 0, 0]
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
        """
        channel1on = self.parameter_values["Channel 1 on voltage [V]"]
        channel1off = self.parameter_values["Channel 1 off voltage [V]"]
        channel2on = self.parameter_values["Channel 2 on voltage [V]"]
        channel2off = self.parameter_values["Channel 2 off voltage [V]"]
        channel3on = self.parameter_values["Channel 3 on voltage [V]"]
        channel3off = self.parameter_values["Channel 3 off voltage [V]"]
        channel4on = self.parameter_values["Channel 4 on voltage [V]"]
        channel4off = self.parameter_values["Channel 4 off voltage [V]"]
        
        channel1delay = self.parameter_values["Channel 1 delay [ms]"]
        channel2delay = self.parameter_values["Channel 2 delay [ms]"]
        channel3delay = self.parameter_values["Channel 3 delay [ms]"]
        channel4delay = self.parameter_values["Channel 4 delay [ms]"]

        self.on_voltages = [channel1on, channel2on, channel3on, channel4on]
        self.off_voltages = [channel1off, channel2off, channel3off, channel4off]
        self.delays = [channel1delay, channel2delay, channel3delay, channel4delay]

        port = self.parameter_values['Port']
        frequency = self.parameter_values['Frequency [Hz]']

        self.symbol_interval = self.parameter_values['Symbol interval [ms]']
        self.injection_duration = self.parameter_values['Injection duration [ms]']
        self.modulation = self.parameter_values["Modulation"]
        self.modulation_index = 4
        self.allowed_symbol_values = [str(val) for val in range(0, self.modulation_index)]

        background_flow_ch_desc = self.parameter_values["Background flow"]
        self.background_flow_channel = ["Channel 1", "Channel 2", "Channel 3", "Channel 4"].index(background_flow_ch_desc)

        if self.modulation == "MoSK" and self.injection_duration > self.symbol_interval:
            Logging.warning("Nonsensical configuration: Injection duration is longer than symbol interval.")

        self.sleep_time = self.symbol_interval

        #Clean up
        if self.transmitters is not None:
            for tx in self.transmitters:
                try:
                    tx.shutdown()
                except:
                    pass

        bartels = BartelsTransmitter(port)
        bartels.micropump_set_frequency(frequency)
        self.transmitters = [bartels]


    def prepare_transmission(self, symbol_values):
        
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
        - This will be called with correct timing
        """

        injection_duration = self.injection_duration
        
        #activate pump according to signal value, keep background flow on
        on_values = self.off_voltages.copy()
        off_values = self.off_voltages.copy()

        if symbol_value > 0:
            #ignore 0 values, as no pump action
            if symbol_value <= self.background_flow_channel:
                #keep background flow constant - ignore pump for symbol values
                symbol_value = symbol_value-1

            on_values[symbol_value] = self.on_voltages[symbol_value]

        on_values[self.background_flow_channel] = self.on_voltages[self.background_flow_channel]
        off_values[self.background_flow_channel] = self.on_voltages[self.background_flow_channel]

        for tx in self.transmitters:
                tx.micropump_set_voltages_with_delay(on_values, off_values, self.delays, injection_duration)


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

        ports, suggested_port = PocketLoCEncoder.available_ports()

        parameters = [
            {
                'description': "Port",
                'dtype': 'item',
                'default': suggested_port,
                'items': [port.name for port in ports],
            },
            {
                'description': "Channel 1 on voltage [V]",
                'dtype': 'int',
                'decimals': 0,
                'default': 250,
                'min': 0,
                'max': 250,
            },
            {
                'description': "Channel 1 off voltage [V]",
                'dtype': 'int',
                'decimals': 0,
                'default': 5,
                'min': 0,
                'max': 250,
            },
            {
                'description': "Channel 1 delay [ms]",
                'dtype': 'int',
                'decimals': 0,
                'default': 0,
                'min': 0,
                'max': 10000,
            },
            {
                'description': "Channel 2 on voltage [V]",
                'dtype': 'int',
                'decimals': 0,
                'default': 150,
                'min': 0,
                'max': 250,
            },
            {
                'description': "Channel 2 off voltage [V]",
                'dtype': 'int',
                'decimals': 0,
                'default': 5,
                'min': 0,
                'max': 250,
            },
            {
                'description': "Channel 2 delay [ms]",
                'dtype': 'int',
                'decimals': 0,
                'default': 0,
                'min': 0,
                'max': 10000,
            },
            {
                'description': "Channel 3 on voltage [V]",
                'dtype': 'int',
                'decimals': 0,
                'default': 150,
                'min': 0,
                'max': 250,
            },
            {
                'description': "Channel 3 off voltage [V]",
                'dtype': 'int',
                'decimals': 0,
                'default': 5,
                'min': 0,
                'max': 250,
            },
            {
                'description': "Channel 3 delay [ms]",
                'dtype': 'int',
                'decimals': 0,
                'default': 0,
                'min': 0,
                'max': 10000,
            },
            {
                'description': "Channel 4 on voltage [V]",
                'dtype': 'int',
                'decimals': 0,
                'default': 150,
                'min': 0,
                'max': 250,
            },
            {
                'description': "Channel 4 off voltage [V]",
                'dtype': 'int',
                'decimals': 0,
                'default': 5,
                'min': 0,
                'max': 250,
            },
            {
                'description': "Channel 4 delay [ms]",
                'dtype': 'int',
                'decimals': 0,
                'default': 0,
                'min': 0,
                'max': 10000,
            },
            {
                'description': "Background flow",
                'dtype': 'item',
                'default': "Channel 1",
                'items': ["Channel 1", "Channel 2", "Channel 3", "Channel 4"]
            },
            {
                'description': "Modulation",
                'dtype': 'item',
                'default': "MoSK",
                'items': ["MoSK"],
            },
            {
                'description': "Frequency [Hz]",
                'dtype': 'int',
                'decimals': 0,
                'default': 50,
                'min': 50,
                'max': 800,
            },
            {
                'description': "Symbol interval [ms]",
                'decimals': 0,
                'dtype': 'float',
                'min': 25,
                'max': 10000,
                'default': 1000,
            },
            {
                'description': "Injection duration [ms]",
                'dtype': 'int',
                'decimals': 0,
                'min': 10,
                'max': 10000,
                'default': 100
            }
        ]
        return parameters


