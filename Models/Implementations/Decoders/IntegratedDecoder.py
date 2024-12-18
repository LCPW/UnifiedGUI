
import scipy.ndimage
import serial
import serial.tools.list_ports
import numpy as np

from Models.Interfaces.DecoderInterface import DecoderInterface
from Models.Implementations.Receivers.IntegratedReceiver import IntegratedReceiver
from Utils import Logging

CLK_IN_MHZ = 40.0


class IntegratedDecoder(DecoderInterface):
    """
    Decoder for the Integrated Decoder
    """
    def __init__(self, parameters, parameter_values):
        super().__init__(parameters, parameter_values)

        super().setup()

    def parameters_edited(self, parameter_values):
        super().parameters_edited(parameter_values)
                
        port = self.parameter_values['port']

        #--------------------------------------------------------------------------------------------------IND
        self.use_ind = self.parameter_values["Use inductive sensor (IND)"]
        deglitch_filter = self.parameter_values["IND Input Deglitch Filter Bandwidth (MHz)"]

        settle_count = self.parameter_values["IND Settle Count"]
        # Settle count allows for the sensor to settle after power up
        # SETTLECOUNT >= floor((Q_sensor * 40MHz) / (16* f_sensor))
        # Q_sensor = Rp*sqrt(C/L)
        # t_settle = Q_sensor / f_sensor = SETTLECOUNT*16/40MHz

        reference_count = self.parameter_values["IND Reference Count"]
        # This is an internal meas averaging - the highest possible value is best
        # R_COUNT = floor(t_count * 40MHz / 16)
        # t_count = 1/f_sample - t_settle - t_switchdelay ---> trade-off between sample rate (f_sample) and sensitivity
        # t_switchdelay = 629ns + 5/40MHz = 754ns

        self.active_ind_channels = self.parameter_values["IND active channels"]

        t_count = reference_count*16/(CLK_IN_MHZ*1000000)
        t_settle = settle_count*16/(CLK_IN_MHZ*1000000)
        t_switchdelay = 0.000000754

        t_sample = (t_count + t_settle + t_switchdelay)*self.active_ind_channels
        #--------------------------------------------------------------------------------------------------IND
        #--------------------------------------------------------------------------------------------------CAP

        self.use_cap = self.parameter_values["Use capacitive sensor (CAP)"]
        conv_time_str = self.parameter_values["CAP conversion time"]

        conversion_time = 0

        if conv_time_str == "11.0ms":
            conversion_time = 0
        elif conv_time_str == "11.9ms":
            conversion_time = 1
        elif conv_time_str == "20.0ms":
            conversion_time = 2
        elif conv_time_str == "38.0ms":
            conversion_time = 3
        elif conv_time_str == "62.0ms":
            conversion_time = 4
        elif conv_time_str == "77.0ms":
            conversion_time = 5
        elif conv_time_str == "92.0ms":
            conversion_time = 6
        elif conv_time_str == "109.6ms":
            conversion_time = 7

        exc_level_str = self.parameter_values["CAP excitation level"]
        excitation_level = 0
        if exc_level_str == "Vdd/8":
            excitation_level = 0
        elif exc_level_str == "Vdd/4":
            excitation_level = 1
        elif exc_level_str == "Vdd*3/8":
            excitation_level = 2
        elif exc_level_str == "Vdd/2":
            excitation_level = 3

        active_channel_str = self.parameter_values["CAP active channel"]
        active_cap_channel = int(active_channel_str)
        diff_mode = self.parameter_values["CAP differential mode"]
        #--------------------------------------------------------------------------------------------------CAP

        if self.use_ind and not self.use_cap:
            Logging.info(f"Approximate inductance sample rate: {1/t_sample:2.2f} Sa/s")

        self.threshold_factor = self.parameter_values["detection threshold factor"]
        self.symbol_duration = self.parameter_values["symbol duration [s]"]

        self.plot_settings = {
            'datalines_active': [[self.use_cap, self.use_ind, self.use_ind and self.active_ind_channels > 1]],
            'datalines_width': 3
        }

        #Clean up
        self.shutdown()

        self.abs_detection_threshold = 0
        self.first_symbol_edge = 0

        # Define receivers list
        receiver = IntegratedReceiver(port, 
                conversion_time, excitation_level, active_cap_channel, diff_mode,
                self.active_ind_channels, CLK_IN_MHZ, deglitch_filter, settle_count, reference_count,
                self.use_cap, self.use_ind)                     
        
        self.receivers = [receiver]
        self.receiver_names = ["Integrated Sensor"]

    def clear(self):
        self.abs_detection_threshold = 0
        self.first_symbol_edge = 0
        return super().clear()

    def calculate_symbol_intervals(self):
        return
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

            min_value = min(self.received[0][0:quiet_stop])
            abs_variation = max(self.received[0][0:quiet_stop]) - min_value

            self.abs_detection_threshold = min_value + abs_variation*self.threshold_factor

        else:
            #find first threshold pass to detect first peak
            threshold_pass = np.argmax(self.received[0] > self.abs_detection_threshold)
            if threshold_pass > 0:
                first_peak_end_limit = np.argmax(self.timestamps[0] > self.timestamps[0][threshold_pass] + self.symbol_duration)
                if first_peak_end_limit > 0:
                    first_peak = np.argmax(self.received[0][threshold_pass:first_peak_end_limit])

                    #center first peak in first symbol interval
                    self.first_symbol_edge = self.timestamps[0][threshold_pass+first_peak] - self.symbol_duration/2
                    self.symbol_intervals = [self.first_symbol_edge]

    def available_ports():
        ports = serial.tools.list_ports.comports()

        if len(ports) == 0:
            Logging.error("No COM ports detected!")
            return

        suggested_port = ports[0].name
        for port in sorted(ports):
            if IntegratedReceiver.HARDWARE_ID in port.hwid:          
                try:
                    serial.Serial(port=port.name, baudrate=IntegratedReceiver.BAUDRATE, timeout=IntegratedReceiver.TIMEOUT)
                except serial.serialutil.SerialException:
                    #Port may be in use or wrong
                    continue
                
                suggested_port = port.name
                break
            
        return ports, suggested_port

    def shutdown(self):
        if self.receivers is not None:
            for rx in self.receivers:
                try:
                    rx.shutdown()
                except:
                    pass

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

    def get_parameters():
        ports, suggested_port = IntegratedDecoder.available_ports()

        parameters = [
            {
                'description': "port",
                'dtype': 'item',
                'default': suggested_port,
                'items': [port.name for port in ports],
            },
            {
                'description': "Use capacitive sensor (CAP)",
                'dtype': 'bool',
                'default': True
            },
            {
                'description': "CAP conversion time",
                'dtype': 'item',
                'items': ['11.0ms', '11.9ms', '20.0ms', '38.0ms', '62.0ms', '77.0ms', '92.0ms', '109.6ms'],
                'default': '11.0ms'
            },
            {
                'description': "CAP excitation level",
                'dtype': 'item',
                'items': ['Vdd/8', 'Vdd/4', 'Vdd*3/8', 'Vdd/2'],
                'default': 'Vdd/2'
            },
            {
                'description': "CAP active channel",
                'dtype': 'item',
                'items': ['1', '2'],
                'default': '1'
            },
            {
                'description': "CAP differential mode",
                'dtype': 'bool',
                'default': False
            },
            {
                'description': "Use inductive sensor (IND)",
                'dtype': 'bool',
                'default': False
            },
            {
                'description': "IND active channels",
                'dtype': 'int',
                'min': 1,
                'max': 2,
                'default': 1,
                'editable': True
            },
            {
                'description': "IND Input Deglitch Filter Bandwidth (MHz)",
                'dtype': 'item',
                'items': ['1.0', '3.3', '10', '33'],
                'default': '3.3',
                'editable': True
            },
            {
                'description': "IND Settle Count",
                'dtype': 'int',
                'min': 2,
                'max': 65535,
                'default': 1024,
                'editable': True,
                'conversion_function': lambda x: str((x*16)/CLK_IN_MHZ) + "us"
            },
            {
                'description': "IND Reference Count",
                'dtype': 'int',
                'min': 5,
                'max': 65535,
                'default': 65535,
                'editable': True,
                'conversion_function': lambda x: str((x*16)/CLK_IN_MHZ) + "us"
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
            }]

        return parameters