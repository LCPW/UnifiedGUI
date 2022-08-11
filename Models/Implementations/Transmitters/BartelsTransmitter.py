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
        self.smp.write(b"P1V10\r\n")
        self.smp.readline().decode("ascii")
        self.portList = []

    def transmit_step(self):
        pass

    def micropump_set_voltage(self, channel, voltage):
        self.smp.write(b"P" + str.encode(str(channel)) + b"V" + str.encode(str(voltage)) + b"\r\n")
        self.smp.readline().decode("ascii")
        # print("Channel: " + str(channel) + " Voltage: " + str(voltage))

    def micropump_set_voltage_duration(self, channel, voltage, duration_ms):
        start = time.time()
        self.smp.write(b"P" + str.encode(str(channel)) + b"V" + str.encode(str(voltage)) + b"\r\n")
        self.smp.readline().decode("ascii")
        start_zero = time.time()
        while (time.time() - start_zero) < (duration_ms/1000):  # ... system time waits until nextsymbol
            pass
        self.smp.write(b"P" + str.encode(str(channel)) + b"V0b\r\n")
        # print("Ende_0V" + str(time.time()-start))

    def micropump_set_frequency(self, frequency):
        self.smp.write(b"F" + str.encode(str(frequency)) + b"\r\n")
        print(self.smp.readline().decode("ascii"))

    def micropump_set_parameters(self, channel, voltage, frequency):
        self.smp.write(b"P" + str.encode(str(channel)) + b"V" + str.encode(str(voltage)) + b"\r\n")
        self.smp.readline().decode("ascii")
        self.smp.write(b"F" + str.encode(str(frequency)) + b"\r\n")
        self.smp.readline().decode("ascii")
        # print("Channel: " + str(channel) + " Voltage: " + str(voltage) + " Frequency: " + str(frequency))

    def onoff(self, channel, voltage, frequency, symbol_value):
        if symbol_value == "on":
            self.micropump_set_parameters(channel, voltage, frequency)
        elif symbol_value == "off":
            self.micropump_set_voltage(channel, 0)

    def modulation_FSK(self, channel, symbol_value, start_time, next_injection_time):

        while (time.time() - start_time) < next_injection_time:  # ... system time waits until nextsymbol
            pass

        timing = time.time() - start_time
        print("next injection: " + str(next_injection_time))
        print("timing: " + str(timing))
        self.micropump_set_voltage_duration(channel, 250, 200)

    def modulation_PSK(self, channel, symbol_value, start_time, next_injection_time, injection):
        while (time.time() - start_time) < next_injection_time + int(symbol_value) * injection:
            pass
        print(int(symbol_value) * injection)
        timing = time.time() - start_time
        print("next injection: " + str(next_injection_time))
        print("timing: " + str(timing))
        self.micropump_set_voltage_duration(channel, 250, 100)

    def modulation_4CSK(self, channel, symbol_value, start_time, next_injection_time):

        # print("Dauer bist nächste Injektion: " + str(next_injection_time - (time.time() - start_time)))
        while (time.time() - start_time) < next_injection_time:  # ... system time waits until nextsymbol
            pass

        timing = time.time() - start_time
        print(next_injection_time)
        print(timing)
        if symbol_value == "00" or symbol_value == "0":  # 00µl
            self.micropump_set_voltage_duration(channel, 0, 0)
        elif symbol_value == "01" or symbol_value == "1":  # 10µl
            self.micropump_set_voltage_duration(channel, 250, 100)
        elif symbol_value == "10" or symbol_value == "2":  # 15µl
            self.micropump_set_voltage_duration(channel, 250, 150)
        elif symbol_value == "11" or symbol_value == "3":  # 20µl
            self.micropump_set_voltage_duration(channel, 250, 200)

    def modulation_8CSK(self, channel, symbol_value, start_time, next_injection_time):
        while (time.time() - start_time) < next_injection_time:  # ... system time waits until nextsymbol
            pass

        if symbol_value == "000" or symbol_value == "0":  # 00µl
            self.micropump_set_voltage_duration(channel, 0, 0)

        elif symbol_value == "001" or symbol_value == "1":  # 05µl
            self.micropump_set_voltage_duration(channel, 130, 100)

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
