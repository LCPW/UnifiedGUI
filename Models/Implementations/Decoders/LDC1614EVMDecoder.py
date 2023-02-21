"""
Author: Benjamin Schiller
E-mail: benjamin.bs.schiller@fau.de
"""
import scipy.ndimage
import serial
import serial.tools.list_ports

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

        self.parameter_values = parameter_values
        self.parameters_edited()

        super().setup()

    def calculate_additional_datalines(self):
        """
        Generates Gaussian filtered version of the datalines.
        Note: Can be optimized by avoiding re-calculating old values every time.
        """
        received = self.decoded['received']
        lengths, timestamps = received['lengths'], received['timestamps']
        for i in range(self.active_channels):
            sensor_values = self.get_received(0, i)
            # No values available
            if sensor_values is None:
                return
            sensor_filtered = scipy.ndimage.gaussian_filter1d(sensor_values, self.sigma)
            dataline = {'length': lengths[0], 'timestamps': timestamps[0][:lengths[0]], 'values': sensor_filtered}
            self.additional_datalines[i] = dataline

    def parameters_edited(self):
        
        self.sigma = self.parameter_values['Sigma']
        
        port = self.parameter_values['port']
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

        self.active_channels = self.parameter_values["active channels"]
        self.additional_datalines_names = ["CH" + str(i) + " Filtered (MHz)" for i in range(4)]


        t_count = reference_count*16/(CLK_IN_MHZ*1000000)
        t_settle = settle_count*16/(CLK_IN_MHZ*1000000)
        t_switchdelay = 0.000000754

        t_sample = (t_count + t_settle + t_switchdelay)*self.active_channels
        Logging.info(f"Approximate sample rate: {1/t_sample:2.2f} Sa/s")


        self.plot_settings = {
            'additional_datalines_active': [True, self.active_channels>1, self.active_channels>2, self.active_channels>3],
            'additional_datalines_width': 3,
            'datalines_active': [[True, self.active_channels>1, self.active_channels>2, self.active_channels>3]],
            'datalines_width': 3
        }

        #Clean up
        self.shutdown()

        # Define receivers list
        receiver = LDC1614EVMReceiver(self.active_channels, CLK_IN_MHZ, port, deglitch_filter, settle_count, reference_count)
        self.receivers = [receiver]
        self.receiver_names = ["LDC1614"]


    def available_ports():
        ports = serial.tools.list_ports.comports()
    
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
                'description': "port",
                'dtype': 'item',
                'default': suggested_port,
                'items': [port.name for port in ports],
            },
            {
                'description': "active channels",
                'dtype': 'int',
                'min': 1,
                'max': 4,
                'default': 1,
                'editable': True
            },
            {
                'description': "Input Deglitch Filter Bandwidth (MHz)",
                'dtype': 'item',
                'items': ['1.0', '3.3', '10', '33'],
                'default': '33',
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