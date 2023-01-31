"""
Author: Max Bartunik
E-mail: max.bartunik@fau.de
"""

import time
import serial.tools.list_ports
import serial
from Utils import Logging

from Models.Interfaces.TransmitterInterface import TransmitterInterface


class IsmatecTransmitter(TransmitterInterface):

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
        self.smp.baudrate = IsmatecTransmitter.BAUDRATE
        self.smp.timeout = IsmatecTransmitter.TIMEOUT
        if not self.smp.is_open:
            try:
                self.smp.open()
            except serial.serialutil.SerialException:
                Logging.error("Cannot connect to selected port.")
                return

        for channel in range(1, 5):
            self.pump_stop(channel)
        

    def shutdown(self):
        for channel in range(1, 5):
            self.pump_stop(channel)

        self.smp.close()

    def to_bytes(input):
        return bytes(str(input), "utf-8")

    def pump_set_constant_rate(self, channel, flow_rate_rpm):
        ch = IsmatecTransmitter.to_bytes(channel)
        self.smp.write(ch + b'L\r') #Set Channel to RPM mode

        flow_rate = IsmatecTransmitter.to_bytes(f"{flow_rate_rpm*100:06.0f}") #Format flow rate as 010000 (6 base 10 chars, 1/100 RPM)
        self.smp.write(ch + b'S' + flow_rate + b'\r') #Set channel RPM rate

    def pump_set_time_rate(self, channel, flow_rate_rpm):
        ch = IsmatecTransmitter.to_bytes(channel)
        self.smp.write(ch + b'N\r') #Set Channel to time mode

        flow_rate = IsmatecTransmitter.to_bytes(f"{flow_rate_rpm*100:06.0f}") #Format flow rate as 010000 (6 base 10 chars, 1/100 RPM)
        self.smp.write(ch + b'xf' + flow_rate + b'\r') #Set channel RPM rate (time mode)

    def pump_set_time_duration(self, channel, pulse_duration_ms):
        ch = IsmatecTransmitter.to_bytes(channel)
        time = IsmatecTransmitter.to_bytes(f"{pulse_duration_ms/100:08.0f}") #Format time as 00000010 (8 base 10 chars, 1/10 s)
        self.smp.write(ch + b'xT' + time + b'\r') #Set pulse on time

    def pump_start(self, channel):
        ch = IsmatecTransmitter.to_bytes(channel)
        self.smp.write(ch + b'H\r') #Start pump/pulse

    def pump_stop(self, channel):
        ch = IsmatecTransmitter.to_bytes(channel)
        self.smp.write(ch + b'I\r') #Stop pump/pulse

