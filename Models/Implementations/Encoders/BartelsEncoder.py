import time

from Models.Interfaces.EncoderInterface import EncoderInterface
from Models.Implementations.Transmitters.BartelsTransmitter import BartelsTransmitter, micropump_find_ports


class BartelsEncoder(EncoderInterface):

    def __init__(self, parameters, parameter_values):
        super().__init__(parameters, parameter_values)
        self.port = parameter_values['port']
        self.bartels = BartelsTransmitter(self.port)
        self.transmitters = [self.bartels]
        self.allowed_sequence_values = [chr(i) for i in range(0, 128)]
        self.voltage = parameter_values['voltage [V]']  # Set micro_pump voltage
        self.frequency = parameter_values['frequency [Hz]']  # Set micro_pump frequency
        self.channel = parameter_values['channel']  # Set Channel 1-4
        self.modulation = parameter_values['modulation']  # 2-ASK (0,1) / 4-ASK (00,01,10,11)
        self.injection_duration = parameter_values['injection duration [ms]']
        # self.sleep_time = parameter_values['character interval [s]']          # Waiting time until next Injection
        self.symbol_interval = parameter_values['symbol interval [ms]']  # Waiting time between Symbols
        self.startTime = time.time()  # Get current system time
        self.binaryOrder = 0  # Only for testing (symbol  number)
        self.next_injection = 0  # Set slots for sending next Injection
        self.modulation_index = 6
        self.time_slot = 0
        self.symbol_distance = 0
        self.parameters_edited()
        super().setup()

        """
        Initialisierung der Mikropumpe
        Aufgaben: 
        - Automatische Suche und Einstellung des richtigen Geräts (port)
        - Übernahme der Anfangsparameter von Spannung, Frequenz, Kanal, Modulation, Symbolinterval
        - Ermittelt aktuelle Systemlaufzeit für die Genauigkeit
        """

    def encode(self, sequence):

        symbol_values = []  # Create list for symbols
        list4csk = []  # Create list for 4-CSK
        list8csk = []  # Create list for 8-CSK
        sequence_in_decimal = [ord(i) for i in sequence]  # Change sequence in decimal (ascii)
        decimal_in_8bit = [format(i, "08b") for i in sequence_in_decimal]  # Change decimal in 8bit sequence
        """
           Informationskodierung in das Binärsystem.
           Aufgaben: 
           - Erstellung jeweilige Binärliste für 4-CSK und 8-CSK
           - Umwandlung von Zeichen in Dezimalzahlen (ascii)
           - Umwandlung von Dezimalzahlen in Binärsequenz (ascii)
           Bsp: A --> 65 --> 01000001 bzw. 
        """

        for x in range(len(decimal_in_8bit)):
            binary8index = [int(a) for a in str(decimal_in_8bit[x])]  # Change 8bit sequence in single Bits

            for i in range(len(binary8index)):
                if self.modulation_index == "2":  # 1Bit --> 1Symbol
                    if i % 8 == 0:
                        continue
                    symbol_values.append(str(binary8index[i]))

                elif self.modulation_index == "4":  # 2Bit --> 1Symbol
                    list4csk.append(str(binary8index[i]))
                    if i % 2 == 1:
                        symbol_values.append(str((list4csk[i - 1]) + (list4csk[i])))

                elif self.modulation_index == "8":  # 3Bit --> 1Symbol
                    list8csk.append(str(binary8index[i]))
                    if i % 3 == 1 and i > 1:
                        symbol_values.append(str((list8csk[i - 2]) + (list8csk[i - 1]) + (list8csk[i])))

                elif self.modulation == "FSK" or self.modulation == "PSK":
                    symbol_values.clear()
                    symbol_values.append(sequence)

            list4csk.clear()
            list8csk.clear()
            # symbol_values.append("-") #Wenn du nach jedem Zeichen ein "-" willst, dann einfach das # entfernen
        if sequence == "":
            symbol_values = 0

        symbol_values.append("-")

        if sequence[0] == "#":
            symbol_values.clear()
            symbol_values = self.individual_encode(sequence, symbol_values)

        self.next_injection = 1  # Restart slots for sending
        self.bartels.micropump_set_frequency(self.frequency)
        self.startTime = time.time()  # Restart system time
        print(symbol_values)
        return symbol_values

    """
    Modulation der Kodierung.
    Aufgaben: 
    - Zusammenfassung von Binärsequenz in Symbole nach jeweiliger Modulation
    Bsp: OOK:    01000001    --> 0,1,0,0,0,0,0,1
         4-CSK:  01000001    --> 01,00,00,01
         8-CSK:  000001      --> 000,001 (weniger Zeichen kodierbar)

    Vorbereitung Transmit
    Aufgaben: 
    - Setzt Zeit für erste Injektion
    - Stellt Frequenz ein
    - Übernimmt aktuelle Systemzeit
    """

    def individual_encode(self, sequence, symbol_values):
        if sequence[1] == "i":
            for i in range(int(sequence[2:])):
                symbol_values.append(1)
                i += 1
            symbol_values.append("-")
        if sequence[1] == "a":
            for i in range(2, len(sequence)):
                symbol_values.append(sequence[i])
        if sequence[1:] == "on" or sequence[1:] == "ON":
            symbol_values.append("on")
        if sequence[1:] == "off" or sequence[1:] == "OFF":
            symbol_values.append("off")
        return symbol_values

    """
       Individuelle Kodierung.
       Aufgaben: 
        - Vorgefertige Kodierungsschemen
    """

    def parameters_edited(self):
        self.channel = self.parameter_values['channel']
        self.frequency = self.parameter_values['frequency [Hz]']
        self.voltage = self.parameter_values['voltage [V]']
        self.port = self.parameter_values['port']
        self.modulation = self.parameter_values['modulation']
        self.symbol_interval = self.parameter_values['symbol interval [ms]']
        self.injection_duration = self.parameter_values['injection duration [ms]']
        # self.time_slot = self.parameter_values['time slot [ms]']
        # self.symbol_distance = self.parameter_values['symbol distance [ms]']
        self.modulation_index = self.parameter_values['modulation index']

        if self.injection_duration + 25 >= self.symbol_interval:
            self.injection_duration = self.symbol_interval - 25
            self.parameter_values['injection duration [ms]'] = self.injection_duration
        if self.modulation == "CSK" and int(self.modulation_index) > 8:
            self.parameter_values['modulation index'] = "8"
            self.modulation_index = "8"

        """
        Aktualisierung Parameter    
        Aufgaben: 
        - Prüft Parameter während der Laufzeit
        - Aktualisiert Parameter für die nächsten Übetragungen (außer Frequenz)
        """

    def transmit_single_symbol_value(self, symbol_value):

        symbol_value = str(symbol_value).strip()

        if not symbol_value == "-":  # If the Symbol 0 or 1 then ...

            if symbol_value == "on" or symbol_value == "off":
                self.bartels.onoff(self.channel, self.voltage, self.frequency, symbol_value)

            elif self.modulation == "CSK":
                if self.modulation_index == "2":
                    while (time.time() - self.startTime) < self.next_injection:  # system time waits until next_symbol
                        pass
                    timing = time.time() - self.startTime  # - self.next_injection
                    print(str(self.binaryOrder) + ". sent: " + str(symbol_value) + "  " + str(timing))  # Testing
                    self.bartels.micropump_set_voltage_duration(self.channel, int(symbol_value) * self.voltage, 10)
                                                               # int(symbol_value) * self.injection_duration)
                    # print("duration: " + str(symbol_value) + "  " + str(time.time() - self.startTime - timing))
                    self.binaryOrder = (self.binaryOrder + 1) % 7  # Testing

                elif self.modulation_index == "4":
                    if self.symbol_interval < 250:
                        self.symbol_interval = 250
                        self.parameter_values['symbol interval [ms]'] = 250
                    self.bartels.modulation_4CSK(self.channel, symbol_value, self.startTime, self.next_injection)

                elif self.modulation_index == "8":
                    if self.symbol_interval < 500:
                        self.symbol_interval = 500
                        self.parameter_values['symbol interval [ms]'] = 500
                    self.bartels.modulation_8CSK(self.channel, symbol_value, self.startTime, self.next_injection)
                self.next_injection = round(self.next_injection + self.symbol_interval / 1000, 3)

            elif self.modulation == "FSK":
                self.bartels.modulation_FSK(self.channel, symbol_value, self.startTime, self.next_injection)
                # next_timeslot = self.time_slot/1000 + int(symbol_value) * self.symbol_distance
                next_timeslot = 0.500 + int(symbol_value) * 0.000
                self.next_injection = round(self.next_injection + next_timeslot, 3)
                print("next timeslot: " + str(next_timeslot))

            elif self.modulation == "PSK":
                injection = 0.000
                print(int(self.modulation_index) - 1)
                self.bartels.modulation_PSK(self.channel, symbol_value, self.startTime, self.next_injection, injection)
                next_timeslot = round(0.500 + (int(self.modulation_index)-1) * injection, 3)
                self.next_injection = round(self.next_injection + next_timeslot, 3)
                print("next timeslot: " + str(next_timeslot))

        else:  # Symbol = "-"
            self.bartels.micropump_set_voltage_duration(self.channel, 0, 0)
            self.next_injection = round(self.next_injection + self.symbol_interval / 1000, 3)

        """"
        Übermittlung der Daten
        Aufgaben: 
        - Prüft Modulationsart
        - Stellt je nach Modulationsart entsprechende Spannung ein
        - Setzt Spannungen je nach Symbolintervall. (Bsp. Änderung jede 100ms)
        Bsp:
        4-CSK:  Vorherige Kodierung: B --> 01000001 --> 01,00,00,10 
                Spannungen: 100V,  0V,  0V, 150V
        """

def get_parameters():
    parameters = [
        {
            'description': "port",
            'dtype': 'string',
            'default': micropump_find_ports(),
            'max_length': 5,
        },

        {
            'description': "channel",
            'dtype': 'item',
            'default': "1",
            'items': ["1", "2", "3", "4"],
        },

        {
            'description': "modulation index",
            'dtype': 'item',
            'default': "2",
            'items': ["2", "4", "8", "16", "32", "64", "128"],
        },

        {
            'description': "modulation",
            'dtype': 'item',
            'default': "CSK",
            'items': ["CSK", "FSK", "PSK"],
        },

        {
            'description': "voltage [V]",
            'dtype': 'int',
            'decimals': 0,
            'default': 250,
            'min': 0,
            'max': 250,
        },

        {
            'description': "frequency [Hz]",
            'dtype': 'int',
            'decimals': 0,
            'default': 70,
            'min': 50,
            'max': 800,
        },

        {
            'description': "symbol interval [ms]",
            'decimals': 0,
            'dtype': 'float',
            'min': 25,
            'max': 10000,
            'default': 100,
        }
        ,
        {
            'description': "injection duration [ms]",
            'dtype': 'int',
            'decimals': 0,
            'min': 10,
            'max': 10000,
            'default': 10,
        },
        # {
        #     'description': "time slot [ms]",
        #     'dtype': 'int',
        #     'decimals': 0,
        #     'min': 1,
        #     'max': 10000,
        #     'default': 50,
        # },
        # {
        #     'description': "symbol distance [ms]",
        #     'dtype': 'int',
        #     'decimals': 0,
        #     'min': 1,
        #     'max': 10000,
        #     'default': 50,
        # },
    ]
    return parameters

