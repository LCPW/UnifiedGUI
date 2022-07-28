import time
import serial.tools.list_ports

from Models.Interfaces.TransmitterInterface import TransmitterInterface

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
        self.portList = []

    def transmit_step(self):
        pass

    def micropump_set_voltage(self, channel, voltage):
        self.smp.write(b"P" + str.encode(str(channel)) + b"V" + str.encode(str(voltage)) + b"\r\n")
        self.smp.readline().decode("ascii")
        # print("Channel: " + str(channel) + " Voltage: " + str(voltage))
        # self.smp.write(b"P" + str.encode(str(channel)) + b"V0b\r\n")
        # self.smp.readline().decode("ascii")
        # print("Channel: " + str(channel) + " Voltage: 0")

    def micropump_set_frequency(self, frequency):
        self.smp.write(b"F" + str.encode(str(frequency)) + b"\r\n")
        print(self.smp.readline().decode("ascii"))

    def micropump_set_parameters(self, channel, voltage, frequency):
        self.smp.write(b"P" + str.encode(str(channel)) + b"V" + str.encode(str(voltage)) + b"\r\n")
        self.smp.readline().decode("ascii")
        self.smp.write(b"F" + str.encode(str(frequency)) + b"\r\n")
        self.smp.readline().decode("ascii")
        # return print("Channel: " + str(channel) + " Voltage: " + str(voltage) + " Frequency: " + str(frequency))

    def modulation_4CSK(self, channel, symbol_value, start_time, next_injection_time):

        injection_duration = 0
        voltage = 225
        print(next_injection_time)
        while (time.time() - start_time) < next_injection_time:         # ... system time waits until nextsymbol
            pass

        timing = time.time() - start_time  # - self.timeNextInjection
        print(timing)

        if symbol_value == " 00":
            voltage = 0
            injection_duration = 0
        if symbol_value == " 01":
            injection_duration = 0.100
        if symbol_value == " 10":
            injection_duration = 0.150
        if symbol_value == " 11":
            injection_duration = 0.200

        self.micropump_set_voltage(channel, voltage)

        start_zero = time.time()
        while (time.time() - start_zero) < injection_duration:  # ... system time waits until nextsymbol
            pass
        self.micropump_set_voltage(channel, 0)

    def modulation_8CSK(self, channel, symbol_value, start_time, next_injection_time):

        injection_duration = 0
        voltage = 225
        print(next_injection_time)
        while (time.time() - start_time) < next_injection_time:         # ... system time waits until nextsymbol
            pass

        timing = time.time() - start_time  # - self.timeNextInjection
        print(timing)

        if symbol_value == " 000":  # 00µl/Injection
            voltage = 0
            injection_duration = 0
        if symbol_value == " 001":  # 5µl/Injection
            injection_duration = 0.050
        if symbol_value == " 010":  # 10µl/Injection
            injection_duration = 0.100
        if symbol_value == " 011":  # 15µl/Injection
            injection_duration = 0.150
        if symbol_value == " 100":  # 20µl/Injection
            injection_duration = 0.200
        if symbol_value == " 101":  # 25µl/Injection
            injection_duration = 0.250
        if symbol_value == " 110":  # 30µl/Injection
            injection_duration = 0.300
        if symbol_value == " 111":  # 35µl/Injection
            injection_duration = 0.350

        self.micropump_set_voltage(channel, voltage)

        start_zero = time.time()
        while (time.time() - start_zero) < injection_duration:  # ... system time waits until nextsymbol
            pass
        self.micropump_set_voltage(channel, 0)

    def manually(self, channel, voltage, frequency, symbol_value):

        if symbol_value == "ON" or symbol_value == "on":
            self.micropump_set_parameters(channel, voltage, frequency)
        elif symbol_value == "OFF" or symbol_value == "off":
            self.micropump_set_parameters(channel, 0, 50)
        else:
            self.micropump_set_parameters(channel, voltage, frequency)
            self.micropump_set_parameters(channel, 0, 50)

    def micropump_find_ports(self):
        portlist = []
        findpump = serial.Serial()

        for onePort in serial.tools.list_ports.comports():
            portlist.append(str(onePort).split(' -'))
            findpump.port = str(portlist[0][0])
            if portlist[0][1].__contains__('Seriell' or 'Serial'):
                if findpump.is_open:
                    try:
                        findpump.write(b"SELECTQUADDRIVER\r\n")
                        if findpump.readline().decode("ascii") == "OK\r\n":
                            return findpump.port
                    finally:
                        print("Port: " + str(findpump.port) + " is checked")
                else:
                    try:
                        findpump.open()
                        findpump.write(b"SELECTQUADDRIVER\r\n")
                        if findpump.readline().decode("ascii") == "OK\r\n":
                            return findpump.port
                        findpump.close()
                    finally:
                        print("Port: " + str(findpump.port) + " is checked")
            portlist.clear()
        return "COM"
