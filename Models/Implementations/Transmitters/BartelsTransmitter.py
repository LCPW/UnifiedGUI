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
        self.smp.write(b"SELECTQUADDRIVER\r\n")
        self.smp.readline().decode("ascii")
        self.smp.write(b"POFF\r\n")
        self.smp.readline().decode("ascii")

    def transmit_step(self):
        pass

    def micropump_set_voltage(self, channel, voltage):
        self.smp.write(b"P" + str.encode(str(channel)) + b"V" + str.encode(str(voltage)) + b"\r\n")
        self.smp.readline().decode("ascii")

    def micropump_set_frequency(self, frequency):
        self.smp.write(b"F" + str.encode(str(frequency)) + b"\r\n")
        self.smp.readline().decode("ascii")

    def micropump_set_parameters(self, channel, voltage, frequency):
        self.smp.write(b"P" + str.encode(str(channel)) + b"V" + str.encode(str(voltage)) + b"\r\n")
        self.smp.readline().decode("ascii")
        self.smp.write(b"F" + str.encode(str(frequency)) + b"\r\n")
        self.smp.readline().decode("ascii")
        #return print("Channel: " + str(channel) + " Voltage: " + str(voltage) + " Frequency: " + str(frequency))
