
import scipy.ndimage
import serial
import serial.tools.list_ports
import numpy as np

from Models.Interfaces.DecoderInterface import DecoderInterface
from Models.Implementations.Receivers.PocketLoCReceiver import PocketLoCReceiver
from Utils import Logging


class PocketLoCDecoder(DecoderInterface):
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
        pass

    def parameters_edited(self):
        
        
        port = self.parameter_values['Port']
        gain = self.parameter_values["Gain"]
        sample_time = self.parameter_values["Sample duration"]

        sensor1 = self.parameter_values["Sensor 1"]
        sensor2 = self.parameter_values["Sensor 2"]
        sensor3 = self.parameter_values["Sensor 3"]
        sensor4 = self.parameter_values["Sensor 4"]
        sensor5 = self.parameter_values["Sensor 5"]
        sensor6 = self.parameter_values["Sensor 6"]


        self.plot_settings = {
            'additional_datalines_active': [],
            'additional_datalines_width': 3,
            'datalines_active': [[True, True, True, True, True, True,True, True, True, True, True, True]],
            'datalines_width': 3
        }

        #Clean up
        self.shutdown()

        # Define receivers list
        receiver = PocketLoCReceiver(port, [sensor1, sensor2, sensor3, sensor4, sensor5, sensor6])

        gain_level = ['0.5x', '1x', '2x', '4x', '8x', '16x', '32x', '64x', '128x', '256x', '512x'].index(gain)

        receiver.set_gain(gain_level)
        receiver.set_sample_time(sample_time)

        self.receivers = [receiver]
        self.receiver_names = ["Colour Sensor"]

    def clear(self):
        return super().clear()

    def available_ports():
        ports = serial.tools.list_ports.comports()

        if len(ports) == 0:
            Logging.error("No COM ports detected!")
            return

        suggested_port = ports[0].name
        for port in sorted(ports):
            if PocketLoCReceiver.HARDWARE_ID in port.hwid:          
                try:
                    serial.Serial(port=port.name, baudrate=PocketLoCReceiver.BAUDRATE, timeout=PocketLoCReceiver.TIMEOUT)
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
                    rx.set_status(True)
                except:
                    pass
    
    def decoder_stopped(self):
        if self.receivers is not None:
            for rx in self.receivers:
                try:
                    rx.set_status(False)
                except:
                    pass

    def get_parameters():
        ports, suggested_port = PocketLoCDecoder.available_ports()

        diode_list = ["F1", "F2", "F3", "F4", "F5", "F6", "F7", "F8", "CLEAR", "NIR"]

        parameters = [
            {
                'description': "Port",
                'dtype': 'item',
                'default': suggested_port,
                'items': [port.name for port in ports],
            },
            {
                'description': "Gain",
                'dtype': 'item',
                'items': ['0.5x', '1x', '2x', '4x', '8x', '16x', '32x', '64x', '128x', '256x', '512x'],
                'default': '16x',
                'editable': True
            },
            {
                'description': "Sample duration",
                'dtype': 'int',
                'min': 1,
                'max': 1000,
                'default': 10,
                'editable': True,
                'conversion_function': lambda x: f"{1000/(x*4):.1f} Sa/s"
            },
            {
                'description': "Sensor 1",
                'dtype': 'item',
                'items': diode_list,
                'default': "F2",
                'editable': True
            },
            {
                'description': "Sensor 2",
                'dtype': 'item',
                'items': diode_list,
                'default': "F3",
                'editable': True
            },
            {
                'description': "Sensor 3",
                'dtype': 'item',
                'items': diode_list,
                'default': "F4",
                'editable': True
            },
            {
                'description': "Sensor 4",
                'dtype': 'item',
                'items': diode_list,
                'default': "F5",
                'editable': True
            },
            {
                'description': "Sensor 5",
                'dtype': 'item',
                'items': diode_list,
                'default': "F7",
                'editable': True
            },
            {
                'description': "Sensor 6",
                'dtype': 'item',
                'items': diode_list,
                'default': "F8",
                'editable': True
            }]

        return parameters