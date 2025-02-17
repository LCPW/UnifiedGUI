"""
Author: Benjamin Schiller / Luiz Wille
E-mail: benjamin.bs.schiller@fau.de / luiz.wille@fau.de
"""
import scipy.ndimage
import serial
import serial.tools.list_ports
import numpy as np

from Models.Interfaces.DecoderInterface import DecoderInterface
from Models.Implementations.Receivers.LDC1614EVMReceiver import LDC1614EVMReceiver
from Utils import Logging

CLK_IN_MHZ = 40.0


class LDC1614EVMDecoder(DecoderInterface):
    """
    Decoder for the Texas Instruments LDC1614 Evaluation Module.
    Datasheet: https://www.ti.com/lit/ds/symlink/ldc1612.pdf
    """
    def __init__(self, parameters, parameter_values):
        super().__init__(parameters, parameter_values)

    def parameters_edited(self, parameter_values):
        super().parameters_edited(parameter_values)

        self.sigma = self.parameter_values['Sigma']
        
        port = self.parameter_values['Port']
        deglitch_filter = self.parameter_values["Input Deglitch Filter Bandwidth (MHz)"]

        settle_count = self.parameter_values["Settle Count"]
        # Settle count allows for the sensor to settle after power up
        # SETTLECOUNT >= floor((Q_sensor * 40MHz) / (16* f_sensor))
        # Q_sensor = Rp*sqrt(C/L)
        # t_settle = Q_sensor / f_sensor = SETTLECOUNT*16/40MHz

        reference_count = self.parameter_values["Reference Count"]
        # This is an internal meas averaging - the highest possible value is best
        # R_COUNT = floor(t_count * 40MHz / 16)
        # t_count = 1/f_sample - t_settle - t_switchdelay ---> trade-off between sample rate (f_sample) and sensitivity
        # t_switchdelay = 629ns + 5/40MHz = 754ns

        self.active_channels = [self.parameter_values['Activate channel 0'], self.parameter_values['Activate channel 1'],
                                self.parameter_values['Activate channel 2'], self.parameter_values['Activate channel 3']]
        self.active_channel_count = self.active_channels.count(True)

        self.additional_datalines_names = ["CH" + str(i) + " Filtered (MHz)" for i in range(4)]

        self.threshold_factor = self.parameter_values["Detection threshold factor"]
        self.symbol_duration = self.parameter_values["Symbol duration [s]"]

        t_conversion = (reference_count*16 + 4) / (CLK_IN_MHZ*1000000)
        t_settle = settle_count*16/(CLK_IN_MHZ*1000000)
        t_switchdelay = 0.000000629 + (5/(CLK_IN_MHZ*1e6))
        t_sample = (t_conversion + t_settle + t_switchdelay)*self.active_channel_count + np.finfo(float).eps
        Logging.info(f"Approximate sample rate: {1/t_sample:2.2f} Sa/s")

        self.plot_settings = {
            'additional_datalines_active': self.active_channels.copy(),
            'additional_datalines_width': 3,
            'datalines_active': [self.active_channels.copy()],
            'datalines_width': 3
        }

        # Clean up
        self.shutdown()

        self.abs_detection_threshold = 0
        self.first_symbol_edge = 0

        # Define receivers list
        if any(active for active in self.active_channels):
            receiver = LDC1614EVMReceiver(self.active_channels, CLK_IN_MHZ, port, deglitch_filter, settle_count, reference_count)
            self.receivers = [receiver]
            self.receiver_names = ["LDC1614"]

        super().setup()

    def calculate_additional_datalines(self):
        """
        Generates Gaussian filtered version of the datalines.
        Note: Can be optimized by avoiding re-calculating old values every time.
        """
        received = self.decoded['received']
        lengths, timestamps = received['lengths'], received['timestamps']
        for idx in range(len(self.active_channels)):
            if self.active_channels[idx]:
                sensor_values = self.get_received(0, idx)
                # No values available
                if sensor_values is None:
                    return
                sensor_filtered = scipy.ndimage.gaussian_filter1d(sensor_values, self.sigma)
                dataline = {'length': lengths[0], 'timestamps': timestamps[0][:lengths[0]], 'values': sensor_filtered}
                self.additional_datalines[idx] = dataline

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
            if LDC1614EVMReceiver.HARDWARE_ID in port.hwid:
                try:
                    serial.Serial(port=port.name, baudrate=LDC1614EVMReceiver.BAUDRATE, timeout=LDC1614EVMReceiver.TIMEOUT)
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
                    rx.set_streaming(False)
                    rx.shutdown()
                except:
                    pass

    def decoder_started(self):
        if self.receivers is not None:
            for rx in self.receivers:
                try:
                    rx.set_streaming(True)
                except:
                    pass
    
    def decoder_stopped(self):
        if self.receivers is not None:
            for rx in self.receivers:
                try:
                    rx.set_streaming(False)
                except:
                    pass

    def get_parameters():
        ports, suggested_port = LDC1614EVMDecoder.available_ports()

        parameters = [
            {
                'description': "Port",
                'dtype': 'item',
                'default': suggested_port,
                'items': [port.name for port in ports],
            },
            {
                'description': "Activate channel 0",
                'dtype': 'bool',
                'default': True
            },
            {
                'description': "Activate channel 1",
                'dtype': 'bool',
                'default': False
            },
            {
                'description': "Activate channel 2",
                'dtype': 'bool',
                'default': False
            },
            {
                'description': "Activate channel 3",
                'dtype': 'bool',
                'default': False
            },
            {
                'description': "Input Deglitch Filter Bandwidth (MHz)",
                'dtype': 'item',
                'items': ['1.0', '3.3', '10', '33'],
                'default': '3.3',
                'editable': True
            },
            {
                'description': "Settle Count",
                'dtype': 'int',
                'min': 2,
                'max': 65535,
                'default': 1024,
                'editable': True,
                'conversion_function': lambda x: str((x*16)/CLK_IN_MHZ) + "us"
            },
            {
                'description': "Reference Count",
                'dtype': 'int',
                'min': 5,
                'max': 65535,
                'default': 65535,
                'editable': True,
                'conversion_function': lambda x: str((x*16)/CLK_IN_MHZ) + "us"
            },
            {
                'description': "Detection threshold factor",
                'decimals': 2,
                'dtype': 'float',
                'min': 1,
                'max': 50,
                'default': 5.0
            },
            {
                'description': "Symbol duration [s]",
                'decimals': 3,
                'dtype': 'float',
                'min': 0.010,
                'max': 20,
                'default': 1
            }]

        parameters.append({
                # Sigma value for Gaussian filter
                'description': "Sigma",
                'decimals': 2,
                'dtype': 'float',
                'min': 0.01,
                'max': 100,
                'default': 2.0,
                'conversion_function': lambda x: str(x*2) + "s"
            })
        return parameters
