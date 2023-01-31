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
        self.smp.write(b"POFF\r\n")
        self.smp.readline().decode("ascii")

    def shutdown(self):
        self.smp.write(b"POFF\r\n")
        self.smp.readline().decode("ascii")

        self.smp.close()

    def micropump_set_voltage(self, channel, voltage):
        """
        set micropump voltage
            parameters:
            channel (int): 1-4
            voltage (int): 0-250
        """
        self.smp.write(b"P" + str.encode(str(channel)) + b"V" + str.encode(str(voltage)) + b"\r\n")
        self.smp.readline().decode("ascii")

    def micropump_set_voltage_duration(self, channel, voltage, duration_ms):
        """
        set micropump frequency
            parameters:
            channel (int):  1-4
            voltage (int):  0-250
            duration (int): 0-10000
        """
        self.micropump_set_voltage(channel, voltage)

        time.sleep(duration_ms/1000)
        self.micropump_set_voltage(channel, 0)

    def micropump_set_frequency(self, frequency):
        """
        set micropump voltage + duration
            parameters:
            frequency (int):  0-850
        """
        self.smp.write(b"F" + str.encode(str(frequency)) + b"\r\n")

    def onoff(self, channel, voltage, frequency, symbol_value):
        """
        set micropump on or off
            parameters:
            channel (int):      1-4
            voltage (int):      0-250
            frequency (int):    0-850
            symbol_value (str): on, off
        """
        if symbol_value == "on":
            self.micropump_set_parameters(channel, voltage, frequency)
        elif symbol_value == "off":
            self.micropump_set_voltage(channel, 0)

