import numpy as np
import serial
import serial.tools.list_ports

from Models.Interfaces.DecoderInterface import DecoderInterface
from Models.Implementations.Receivers.AD7746Receiver import AD7746Receiver
from Utils import Logging

NEGATIVE_DETECTION_THRESHOLD = True

class AD7746Decoder(DecoderInterface):
    def __init__(self, parameters, parameter_values):
        super().__init__(parameters, parameter_values)
        super().setup()

    def parameters_edited(self, parameter_values):
        super().parameters_edited(parameter_values)

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

        self.threshold_factor = self.parameter_values["detection threshold factor"]
        self.symbol_duration = self.parameter_values["symbol duration [s]"]

        #Clean up
        self.shutdown()

        self.abs_detection_threshold = 0
        self.first_symbol_edge = 0

        receiver = AD7746Receiver(self.port, self.conversion_time, self.excitation_level, self.active_channel, self.diff_mode)
        self.receivers = [receiver]
        self.receiver_names = ["AD7746"]

    def clear(self):
        self.abs_detection_threshold = 0
        self.abs_variation = 0
        self.first_symbol_edge = 0
        return super().clear()

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


    def pre_processing(self):
        pass

    def calculate_additional_datalines(self):
        pass

    def calculate_landmarks(self):
        pass

    def calculate_symbol_intervals(self):
        ref_threshold_length = 2 #seconds

        if self.first_symbol_edge > 0:
            next_edge = self.symbol_intervals[-1] + self.symbol_duration
            if self.max_timestamp > next_edge:
                self.symbol_intervals.append(next_edge)
            
            return
        
        if self.max_timestamp - self.min_timestamp < ref_threshold_length:
            #We have to wait for enough samples
            return
        elif self.abs_detection_threshold == 0:
            #Use start of transmission to determine a first peak threshold
            quiet_stop = np.argmax(self.timestamps[0] > self.min_timestamp + ref_threshold_length)
            
            max_value = max(self.received[0][0:quiet_stop])
            min_value = min(self.received[0][0:quiet_stop])
            self.abs_variation = max_value - min_value

            if NEGATIVE_DETECTION_THRESHOLD:
                self.abs_detection_threshold = max_value - self.abs_variation*(self.threshold_factor + 0.5)
            else:
                self.abs_detection_threshold = min_value + self.abs_variation*(self.threshold_factor + 0.5)

        else:
            #find first threshold pass to detect first peak
            threshold_pass = 0
            if NEGATIVE_DETECTION_THRESHOLD:
                threshold_pass = np.argmax(self.received[0] < self.abs_detection_threshold)
            else:
                threshold_pass = np.argmax(self.received[0] > self.abs_detection_threshold)

            if threshold_pass > 0:
                first_peak_end_limit = np.argmax(self.timestamps[0] > self.timestamps[0][threshold_pass] + self.symbol_duration)
                if first_peak_end_limit > 0:
                    first_peak = 0
                    if NEGATIVE_DETECTION_THRESHOLD:
                        first_peak = np.argmin(self.received[0][threshold_pass:first_peak_end_limit])
                    else:
                        first_peak = np.argmax(self.received[0][threshold_pass:first_peak_end_limit])

                    #center first peak in first symbol interval
                    self.first_symbol_edge = self.timestamps[0][threshold_pass+first_peak] - self.symbol_duration/2
                    self.symbol_intervals = [self.first_symbol_edge]

    def calculate_symbol_values(self):
        
        if len(self.symbol_intervals)-1 > len(self.symbol_values):
            start_time = self.symbol_intervals[-2]
            end_time = self.symbol_intervals[-1]

            start_index = np.argmax(self.timestamps[0] > start_time)
            end_index = np.argmax(self.timestamps[0] > end_time)

            if start_index == 0 or start_index == end_index:
                return

            interval_data = self.received[0][start_index:end_index]

            #So far only binary CSK
            symbol_value = self.binary_threshold_detection(interval_data)
        
            self.symbol_values.append(symbol_value)

    def binary_threshold_detection(self, interval_data):
        if NEGATIVE_DETECTION_THRESHOLD:
            #Downward symbols
            min_index = np.argmin(interval_data)
            if min_index > 0 and max(interval_data[0:min_index]) > interval_data[min_index] + self.abs_variation*self.threshold_factor:
                return 1
        else:
            max_index = np.argmax(interval_data)
            if max_index > 0 and min(interval_data[0:max_index]) < interval_data[max_index] - self.abs_variation*self.threshold_factor:
                return 1
        
        return 0

    def calculate_sequence(self):

        #binary CSK
        sync_symbols = 3
        symbol_length = 8

        received_seq_length = np.floor((len(self.symbol_values)-3)/symbol_length)

        if received_seq_length > 0 and received_seq_length > len(self.sequence):
            #We have something to decode

            seq_start = len(self.sequence)*symbol_length+sync_symbols

            chr_value = 0

            for i in range(symbol_length):
                chr_value += (self.symbol_values[seq_start+i]<<(7-i))

            self.sequence += chr(chr_value)

    def shutdown(self):
        if self.receivers is not None:
            for rx in self.receivers:
                try:
                    rx.shutdown()
                except:
                    pass

    def available_ports():
        ports = serial.tools.list_ports.comports()

        if len(ports) == 0:
            Logging.error("No COM ports detected!")
            return
    
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
                read_id = conn.readline().decode('utf-8').replace("\r\n", "")
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
            },
            {
                'description': "detection threshold factor",
                'decimals': 2,
                'dtype': 'float',
                'min': 1,
                'max': 50,
                'default': 5.0
            },
            {
                'description': "symbol duration [s]",
                'decimals': 3,
                'dtype': 'float',
                'min': 0.010,
                'max': 20,
                'default': 1
            }
        ]
        return parameters