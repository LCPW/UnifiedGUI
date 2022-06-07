import sys
import time
import serial.tools.list_ports

from Models.Interfaces.TransmitterInterface import TransmitterInterface

from Utils import Queue


class BartelsTransmitter(TransmitterInterface):
    smp = serial.Serial()

    def __init__(self, initial_value):
        super().__init__()
        self.value = initial_value
        self.smp.port = "COM15"
        if self.smp.is_open == False:
            self.smp.open()
        self.smp.write(b"QUADDRIVER\r\n")
        self.smp.readline().decode("ascii")
        self.smp.write(b"POFF\r\n")
        self.smp.readline().decode("ascii")

    def transmit_step(self):
        timestamp = time.time()
        Queue.queue.put((self.value, timestamp))