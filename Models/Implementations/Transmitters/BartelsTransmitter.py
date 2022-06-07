import time
import serial.tools.list_ports

from Models.Interfaces.TransmitterInterface import TransmitterInterface
from Utils import Queue


class BartelsTransmitter(TransmitterInterface):
    smp = serial.Serial()

    def __init__(self, port):
        super().__init__()
        self.value = 0
        self.smp.port = str(port)
        if not self.smp.is_open:
            self.smp.open()
        self.smp.write(b"QUADDRIVER\r\n")
        self.smp.readline().decode("ascii")
        self.smp.write(b"POFF\r\n")
        self.smp.readline().decode("ascii")

    def transmit_step(self):
        timestamp = time.time()
        Queue.queue.put((self.value, timestamp))

