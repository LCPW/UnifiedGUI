"""
Author: Max Bartunik
E-mail: max.bartunik@fau.de
"""

import time
import serial.tools.list_ports
import serial
from Utils import Logging

from Models.Interfaces.TransmitterInterface import TransmitterInterface


class FraunhoferTransmitter(TransmitterInterface):

    BAUDRATE = 38400
    TIMEOUT = 0.1 #s

    def __init__(self, port):
        """
        Initialization of the Transmitter
        - switch channels off
        """
        super().__init__()

        self.smp = serial.Serial()
        self.smp.port = str(port)
        self.smp.baudrate = FraunhoferTransmitter.BAUDRATE
        self.smp.timeout = FraunhoferTransmitter.TIMEOUT
        if not self.smp.is_open:
            try:
                self.smp.open()
            except serial.serialutil.SerialException:
                Logging.error("Cannot connect to selected port.")
                return

        self.hv_off()
        

    def shutdown(self):
        self.hv_off()
        self.smp.close()

    def set_frequency(self, frequency):
        data = 'setF:' + str(frequency) + '\n'
        self.smp.write(data.encode('utf-8'))

    def hv_on(self):
        self.smp.write(b'setStatus:1\n')

    def hv_off(self):
        self.smp.write(b'setStatus:0\n')

    def set_voltage(self, max_voltage):
        maxCmd = 'setV+:' + str(max_voltage) + '\n'
        minCmd = b'setV-:-80\n'

        self.smp.write(maxCmd.encode('utf-8'))
        self.smp.write(minCmd)

    def set_burst_mode(self):
        modeCmd = b'setMode:3\n' # 1: normal mode, 2: continous mode, 3: burst mode, 4: custom mode
        self.smp.write(modeCmd)

    def send_burst(self, burst_count):
        if burst_count == 0:
            return

        burstCmd = 'setBurstCount:' + str(burst_count) + "\n"
        self.smp.write(burstCmd.encode("utf-8"))

        self.smp.write(b'Trigger\n')

