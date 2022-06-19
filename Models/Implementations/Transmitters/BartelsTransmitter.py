import time
import serial.tools.list_ports

from Models.Interfaces.TransmitterInterface import TransmitterInterface

timezero = time.time()


class BartelsTransmitter(TransmitterInterface):

    def __init__(self, port):
        super().__init__()
        self.smp = serial.Serial()
        self.value = 0
        self.smp.port = str(port)
        if not self.smp.is_open:
            self.smp.open()
        self.smp.write(b"QUADDRIVER\r\n")
        self.smp.readline().decode("ascii")
        self.smp.write(b"POFF\r\n")
        self.smp.readline().decode("ascii")

    def transmit_step(self):
        pass

    def micropump(self, channel, voltage, frequency):
        self.smp.write(b"P" + str.encode(str(channel)) + b"V" + str.encode(str(voltage)) + b"\r\n")
        self.smp.readline().decode("ascii")
        self.smp.write(b"F" + str.encode(str(frequency)) + b"\r\n")
        self.smp.readline().decode("ascii")
        #return print("Channel: " + str(channel) + " Voltage: " + str(voltage) + " Frequency: " + str(frequency))
