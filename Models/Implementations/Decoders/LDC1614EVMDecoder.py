"""
Author: Benjamin Schiller
E-mail: benjamin.bs.schiller@fau.de
"""
import scipy.ndimage

from Models.Interfaces.DecoderInterface import DecoderInterface


class LDC1614EVMDecoder(DecoderInterface):
    """
    Decoder for the Texas Instruments LDC1614 Evaluation Module.
    Datasheet: https://www.ti.com/lit/ds/symlink/ldc1612.pdf
    """
    def __init__(self, parameters, parameter_values):
        super().__init__(parameters, parameter_values)

        self.sigma = parameter_values['Sigma']

        # Implement: Define receivers list
        self.receiver_types = ["LDC1614EVMReceiver"]

        self.num_sensors = 4
        self.additional_datalines_names = ["Sensor CH" + str(i) + " Filtered (Hz)" for i in range(self.num_sensors)]
        self.plot_settings = {
            'additional_datalines_active': [True, True, False, False],
            'additional_datalines_width': 3,
            'datalines_active': [[True, True, False, False]],
            'datalines_width': 3
        }

        super().setup()

    def calculate_additional_datalines(self):
        received = self.decoded['received']
        lengths, timestamps, values = received['lengths'], received['timestamps'], received['values']
        if lengths[0] == 0:
            return
        for i in range(self.num_sensors):
            sensor = values[0][:lengths[0], i]
            sensor_filtered = scipy.ndimage.gaussian_filter1d(sensor, self.sigma)
            dataline = {'length': lengths[0], 'timestamps': timestamps[0][:lengths[0]], 'values': sensor_filtered}
            self.additional_datalines[i] = dataline


def get_parameters():
    parameters = [
        {
            # Sigma value for Gaussian filter
            'description': "Sigma",
            'decimals': 2,
            'dtype': 'float',
            'min': 0,
            'max': 100,
            'default': 2.0,
        }]
    return parameters