"""
Author: Steve Kungu
E-mail: steve.kungu@fau.de
"""

import time
import serial.tools.list_ports

from Models.Interfaces.TransmitterInterface import TransmitterInterface


class BartelsTransmitter(TransmitterInterface):

    def __init__(self, port):
        """
        Initialization of the Transmitter
        - select Highdriver
        - switch channels off
        """
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
        self.smp.write(b"P" + str.encode(str(channel)) + b"V" + str.encode(str(voltage)) + b"\r\n")
        self.smp.readline().decode("ascii")
        start_zero = time.time()
        while (time.time() - start_zero) < (duration_ms/1000):  # ... system time waits until nextsymbol
            pass
        self.smp.write(b"P" + str.encode(str(channel)) + b"V0b\r\n")

    def micropump_set_frequency(self, frequency):
        """
        set micropump voltage + duration
            parameters:
            frequency (int):  0-850
        """
        self.smp.write(b"F" + str.encode(str(frequency)) + b"\r\n")

    def micropump_set_parameters(self, channel, voltage, frequency):
        """
        set micropump voltage + frequency
            parameters:
            channel (int):      1-4
            voltage (int):      0-250
            frequency (int):    0-850
        """
        self.smp.write(b"P" + str.encode(str(channel)) + b"V" + str.encode(str(voltage)) + b"\r\n")
        self.smp.readline().decode("ascii")
        self.smp.write(b"F" + str.encode(str(frequency)) + b"\r\n")
        self.smp.readline().decode("ascii")

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

    def modulation_TSK(self, channel, symbol_value, start_time, next_injection_time, voltage, duration):
        """
        place injections with TSK modulation.
            parameters:
            channel (int):              1-4
            symbol_value (float):       0-1023
            start_time (float):         start time when decoding
            next_injection_time (int):  injection time = b + e * Symbol
            voltage (int):              0-250
            duration (int):             0-10000
            b = basetime
            e = extratime
        """
        while (time.time() - start_time) < next_injection_time:
            pass  # wait until next injection time
        self.micropump_set_voltage_duration(channel, voltage, duration)

    def modulation_PSK(self, channel, symbol_value, start_time, symbol_interval, injection_time, voltage, duration):
        """
        place injections with PSK modulation.
            parameters:
            channel (int):              1-4
            symbol_value (float):       0-1023
            start_time (float):         start time when decoding
            symbol interval (int):      rolling interval time = b + e * (M-1)
            injection_time (int):       injection time = symbol interval + e * Symbol
            voltage (int):              0-250
            duration (int):             0-10000
            b = basetime
            e = extratime
            M = modulationindex
        """
        while (time.time() - start_time) < symbol_interval + int(symbol_value) * injection_time:
            pass  # wait until next injection time
        self.micropump_set_voltage_duration(channel, voltage, duration)

    def modulation_4CSK(self, channel, symbol_value, start_time, next_injection_time):
        """
        place injections with 4CSK modulation and predefined injection quantity
            parameters:
            channel (int):              1-4
            symbol_value (str):         00,01,10,11 or 0-3
            start_time (float):         start time when decoding
            next_injection_time (int):  injection time (rolling)
        """
        while (time.time() - start_time) < next_injection_time:
            pass  # wait until next injection time

        if symbol_value == "00" or symbol_value == "0":  # 00µl
            self.micropump_set_voltage_duration(channel, 0, 0)
        elif symbol_value == "01" or symbol_value == "1":  # 10µl
            self.micropump_set_voltage_duration(channel, 250, 100)
        elif symbol_value == "10" or symbol_value == "2":  # 15µl
            self.micropump_set_voltage_duration(channel, 250, 150)
        elif symbol_value == "11" or symbol_value == "3":  # 20µl
            self.micropump_set_voltage_duration(channel, 250, 200)

    def modulation_8CSK(self, channel, symbol_value, start_time, next_injection_time):
        """
       place injections with 8CSK modulation and predefined injection quantity
           parameters:
           channel (int):              1-8
           symbol_value (str):         000,001,010,011,100,101,110,111 or 0-7
           start_time (float):         start time when decoding
           next_injection_time (int):  injection time (rolling)
        """
        while (time.time() - start_time) < next_injection_time:  # wait until next injection time
            pass

        if symbol_value == "000" or symbol_value == "0":  # 00µl
            self.micropump_set_voltage_duration(channel, 0, 0)

        elif symbol_value == "001" or symbol_value == "1":  # 05µl
            self.micropump_set_voltage_duration(channel, 250, 50)

        elif symbol_value == "010" or symbol_value == "2":  # 10µl
            self.micropump_set_voltage_duration(channel, 250, 100)

        elif symbol_value == "011" or symbol_value == "3":  # 15µl
            self.micropump_set_voltage_duration(channel, 250, 150)

        elif symbol_value == "100" or symbol_value == "4":  # 20µl
            self.micropump_set_voltage_duration(channel, 250, 200)

        elif symbol_value == "101" or symbol_value == "5":  # 25µl
            self.micropump_set_voltage_duration(channel, 250, 250)

        elif symbol_value == "110" or symbol_value == "6":  # 30µl
            self.micropump_set_voltage_duration(channel, 250, 300)

        elif symbol_value == "111" or symbol_value == "7":  # 35µl
            self.micropump_set_voltage_duration(channel, 250, 350)


def micropump_find_ports():
    """
        search port from computer
        return (str): "COM" + port
    """
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
