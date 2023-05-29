"""
Author: Steve Kungu
E-mail: steve.kungu@fau.de
"""

import time
import serial.tools.list_ports
import serial
from Utils import Logging

from Models.Interfaces.TransmitterInterface import TransmitterInterface


class BartelsTransmitter(TransmitterInterface):

    HARDWARE_ID = "2341:8037"
    DEVICE_ID = "PocketLoCPumpController"
    BAUDRATE = 9600
    TIMEOUT = 0.1 #s

    def __init__(self, port):
        """
        Initialization of the Transmitter
        - select Highdriver
        - switch channels off
        """
        super().__init__()

        self.smp = serial.Serial()
        self.smp.port = str(port)
        self.smp.baudrate = BartelsTransmitter.BAUDRATE
        self.smp.timeout = BartelsTransmitter.TIMEOUT
        if not self.smp.is_open:
            try:
                self.smp.open()
            except serial.serialutil.SerialException:
                Logging.error("Cannot connect to selected port.")
                return

        self.smp.write(str.encode("ID\r\n"))
        read_id = self.smp.readline().decode('utf-8').replace("\r\n", "")
        if read_id != BartelsTransmitter.DEVICE_ID:
            Logging.warning("Unexpected device ID. Are you sure you are connected to the correct port?")

        self.smp.write(b"SELECTQUADDRIVER\r\n")
        self.smp.readline().decode("ascii")
        self.micropump_set_state(False)

    def shutdown(self):
        self.micropump_set_state(False)

        self.smp.close()

    def micropump_set_state(self, on):
        if on:
            self.smp.write(b"PON\r\n")
            self.smp.readline().decode("ascii")
        else:
            self.smp.write(b"POFF\r\n")
            self.smp.readline().decode("ascii")
            self.smp.write(b"PA000#000#000#000\r\n")
            self.smp.readline().decode("ascii")
        

    def micropump_set_voltage(self, channels, voltage):
        """
        set micropump voltage
            parameters:
            active channels (array of ints): [1, 0, 0, 0]
            voltage (int): 0-250
        """

        # PA<aaa>#<bbb>#<ccc>#<ddd>
        # Set the voltage of all four pumps (<aaa> for pump 1, <bbb> for pump 2, ...). Each value must be zero-padded to exactly three characters.
        command = "PA{:03d}#{:03d}#{:03d}#{:03d}\r\n".format(voltage*channels[0], voltage*channels[1], voltage*channels[2], voltage*channels[3])

        self.smp.write(str.encode(command))
        self.smp.readline().decode("ascii")

    def micropump_set_voltage_duration(self, channel1, channel2, channel3, channel4, voltage, duration_ms):
        """
        set micropump frequency
            parameters:
            channel (int):  1-4
            voltage (int):  0-250
            duration (int): 0-10000
        """
        if duration_ms == 0:
            return
        
        channels = [int(channel1), int(channel2), int(channel3), int(channel4)]

        self.micropump_set_voltage(channels, voltage)

        time.sleep(duration_ms/1000)
        self.micropump_set_voltage(channels, 0)

    def micropump_set_frequency(self, frequency):
        """
        set micropump voltage + duration
            parameters:
            frequency (int):  0-850
        """
        self.smp.write(b"F" + str.encode(str(frequency)) + b"\r\n")

