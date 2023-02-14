"""
Author: Benjamin Schiller
E-mail: benjamin.bs.schiller@fau.de
"""
import scipy.ndimage

from Models.Interfaces.DecoderInterface import DecoderInterface
from Models.Implementations.Receivers.LDC1614EVMReceiver import LDC1614EVMReceiver


RECEIVER0_NUM_CHANNELS = 4
CLK_IN_MHZ = 40.0


class LDC1614EVMDecoder(DecoderInterface):
    """
    Decoder for the Texas Instruments LDC1614 Evaluation Module.
    Datasheet: https://www.ti.com/lit/ds/symlink/ldc1612.pdf
    """
    def __init__(self, parameters, parameter_values):
        super().__init__(parameters, parameter_values)

        self.sigma = parameter_values['Sigma']
        com_port = parameter_values['COM Port']
        deglitch_filters = parameter_values["Input Deglitch Filter Bandwidth (MHz)"]
        settle_counts = [parameter_values["Settle Count CH" + str(c)] for c in range(RECEIVER0_NUM_CHANNELS)]
        reference_counts = [parameter_values["Reference Count CH" + str(c)] for c in range(RECEIVER0_NUM_CHANNELS)]
        low_power_activation_mode = parameter_values["Low Power Activation Mode"]
        drive_current = [parameter_values["Drive Current CH" + str(c)] for c in range(RECEIVER0_NUM_CHANNELS)]

        # Define receivers list
        self.receivers = [LDC1614EVMReceiver(RECEIVER0_NUM_CHANNELS, CLK_IN_MHZ, com_port, deglitch_filters, settle_counts, reference_counts, low_power_activation_mode, drive_current)]

        self.additional_datalines_names = ["Sensor CH" + str(i) + " Filtered (MHz)" for i in range(RECEIVER0_NUM_CHANNELS)]
        self.plot_settings = {
            'additional_datalines_active': [True, True, False, False],
            'additional_datalines_width': 3,
            'datalines_active': [[True, True, False, False]],
            'datalines_width': 3
        }

        super().setup()

    def calculate_additional_datalines(self):
        """
        Generates Gaussian filtered version of the datalines.
        Note: Can be optimized by avoiding re-calculating old values every time.
        """
        received = self.decoded['received']
        lengths, timestamps = received['lengths'], received['timestamps']
        for i in range(RECEIVER0_NUM_CHANNELS):
            sensor_values = self.get_received(0, i)
            # No values available
            if sensor_values is None:
                return
            sensor_filtered = scipy.ndimage.gaussian_filter1d(sensor_values, self.sigma)
            dataline = {'length': lengths[0], 'timestamps': timestamps[0][:lengths[0]], 'values': sensor_filtered}
            self.additional_datalines[i] = dataline

    def parameters_edited(self):
        self.sigma = self.parameter_values['Sigma']


    def get_parameters():
        parameters = [
            {
                'description': "COM Port",
                'dtype': 'int',
                'min': 0,
                'max': 100,
                'default': 3,
                'editable': False
            },
            {
                'description': "Input Deglitch Filter Bandwidth (MHz)",
                'dtype': 'item',
                'items': ['1.0', '3.3', '10', '33'],
                'default': '33',
                'editable': False
            },
            {
                'description': "Low Power Activation Mode",
                'dtype': 'bool',
                'default': False,
                'editable': False
            }]

        for c in range(RECEIVER0_NUM_CHANNELS):
            parameters.append({
                'description': "Settle Count CH" + str(c),
                'dtype': 'int',
                'min': 0,
                'max': 65535,
                'default': 1024,
                'editable': False,
                'conversion_function': lambda x: "Settling Time: " + str((x*16)/CLK_IN_MHZ) + "us"
            })

        for c in range(RECEIVER0_NUM_CHANNELS):
            parameters.append({
                'description': "Reference Count CH" + str(c),
                'dtype': 'int',
                'min': 0,
                'max': 65535,
                'default': 65535,
                'editable': False,
                'conversion_function': lambda x: "Conversion Time: " + str((x*16 + 4)/CLK_IN_MHZ) + "us"
            })

        for c in range(RECEIVER0_NUM_CHANNELS):
            parameters.append({
                'description': "Drive Current CH" + str(c),
                'dtype': 'int',
                'min': -1,
                'max': 31,
                'default': -1,
                'editable': False
            })

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