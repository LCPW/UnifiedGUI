

import numpy as np
import serial
import serial.tools.list_ports

from Models.Interfaces.DecoderInterface import DecoderInterface
from Models.Implementations.Receivers.AD7746Receiver import AD7746Receiver


class AD7746Decoder(DecoderInterface):
    def __init__(self, parameters, parameter_values):
        super().__init__(parameters, parameter_values)

        self.parameter_values = parameter_values
        self.parameters_edited()

        super().setup()

    def parameters_edited(self):
        self.port = self.parameter_values["port"]
        conv_time_str = self.parameter_values["conversion time"]

        if conv_time_str == "11.0ms":
            self.conversion_time = 0
        elif conv_time_str == "11.9ms":
            self.conversion_time = 1
        elif conv_time_str == "20.0ms":
            self.conversion_time = 2
        elif conv_time_str == "38.0ms":
            self.conversion_time = 3
        elif conv_time_str == "62.0ms":
            self.conversion_time = 4
        elif conv_time_str == "77.0ms":
            self.conversion_time = 5
        elif conv_time_str == "92.0ms":
            self.conversion_time = 6
        elif conv_time_str == "109.6ms":
            self.conversion_time = 7

        exc_level_str = self.parameter_values["excitation level"]

        if exc_level_str == "Vdd/8":
            self.excitation_level = 0
        elif exc_level_str == "Vdd/4":
            self.excitation_level = 1
        elif exc_level_str == "Vdd*3/8":
            self.excitation_level = 2
        elif exc_level_str == "Vdd/2":
            self.excitation_level = 3

        active_channel_str = self.parameter_values["active channel"]
        self.active_channel = int(active_channel_str)
        self.diff_mode = self.parameter_values["differential mode"]

        #Clean up
        if self.receivers is not None:
            for rx in self.receivers:
                try:
                    rx.shutdown()
                except:
                    pass

        receiver = AD7746Receiver(self.port, self.conversion_time, self.excitation_level, self.active_channel, self.diff_mode)
        self.receivers = [receiver]
        self.receiver_names = ["AD7746"]

    def decoder_started(self):
        self.set_rx_status(True)
    
    def decoder_stopped(self):
        self.set_rx_status(False)

    def set_rx_status(self, status):
        if self.receivers is not None:
            for rx in self.receivers:
                try:
                    rx.set_status(status)
                except:
                    pass

    def calculate_symbol_intervals(self):
        l = self.lengths[0]
        if l > 0:
            difference = self.received[0][1:l] - self.received[0][0:l-1]
            indices = list(np.nonzero(np.array(difference))[0])
            self.symbol_intervals = [self.timestamps[0][i] for i in indices]

    def calculate_symbol_values(self):
        for i in range(len(self.symbol_values), len(self.symbol_intervals) - 1):
            left_index = np.argmin(list(map(abs, self.timestamps[0][:self.lengths[0]] - self.symbol_intervals[i])))
            right_index = np.argmin(list(map(abs, self.timestamps[0][:self.lengths[0]] - self.symbol_intervals[i + 1])))

            max_tmp = int(np.round(np.mean(self.received[0][left_index:right_index])))
            self.symbol_values += [max_tmp]

    def calculate_sequence(self):
        symbol_length = 7
        length = max(0, len(self.symbol_values) - symbol_length * 2)
        for i in range(len(self.sequence) * symbol_length * 2, length, symbol_length * 2):
            vs = self.symbol_values[i:i + symbol_length * 2]
            vs = [v-1 for v in vs if v > 0]
            c = 0
            for bit in vs:
                c = c * 2 + bit
            self.sequence += chr(c)


    def available_ports():
        ports = serial.tools.list_ports.comports()
    
        suggested_port = ports[0].name
        for port in sorted(ports):
            if AD7746Receiver.HARDWARE_ID in port.hwid:
                conn = None            
                try:
                    conn = serial.Serial(port=port.name, baudrate=AD7746Receiver.BAUDRATE, timeout=AD7746Receiver.TIMEOUT)
                except serial.serialutil.SerialException:
                    #Port may be in use or wrong
                    continue
                
                conn.write(b"ID\r\n")
                read_id = conn.readline().decode('utf-8') #.replace("\r\n", "")
                read_id2 = conn.readline().decode('utf-8')
                read_id3 = conn.readline().decode('utf-8')
                read_id4 = conn.readline().decode('utf-8')
                read_id5 = conn.readline().decode('utf-8')
                conn.close()
                if read_id == AD7746Receiver.DEVICE_ID:
                    suggested_port = port.name
                    break
            
        return ports, suggested_port


    def get_parameters():
        ports, suggested_port = AD7746Decoder.available_ports()

        parameters = [
            {
                'description': "port",
                'dtype': 'item',
                'default': suggested_port,
                'items': [port.name for port in ports],
            },
            {
                'description': "conversion time",
                'dtype': 'item',
                'items': ['11.0ms', '11.9ms', '20.0ms', '38.0ms', '62.0ms', '77.0ms', '92.0ms', '109.6ms'],
                'default': '11.0ms'
            },
            {
                'description': "excitation level",
                'dtype': 'item',
                'items': ['Vdd/8', 'Vdd/4', 'Vdd*3/8', 'Vdd/2'],
                'default': 'Vdd/2'
            },
            {
                'description': "active channel",
                'dtype': 'item',
                'items': ['1', '2'],
                'default': '2'
            },
            {
                'description': "differential mode",
                'dtype': 'bool',
                'default': False
            }
        ]
        return parameters