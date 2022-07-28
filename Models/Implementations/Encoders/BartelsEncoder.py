import time

from Models.Interfaces.EncoderInterface import EncoderInterface
from Models.Implementations.Transmitters.BartelsTransmitter import BartelsTransmitter


class BartelsEncoder(EncoderInterface):

    def __init__(self, parameters, parameter_values):
        super().__init__(parameters, parameter_values)
        self.port = parameter_values['port']
        self.bartels = BartelsTransmitter(self.port)
        self.transmitters = [self.bartels]
        self.allowed_sequence_values = [chr(i) for i in range(0, 128)]
        self.voltage = parameter_values['voltage [V]']                          # Set micropump voltage
        self.frequency = parameter_values['frequency [Hz]']                     # Set micropump frequency
        self.channel = parameter_values['channel']                              # Set Channel 1-4
        self.modulation = parameter_values['modulation']                        # 2-ASK (0,1) / 4-ASK (00,01,10,11)
        # self.sleep_time = parameter_values['character interval [s]']          # Waiting time until next Injection
        self.symbolInterval = parameter_values['symbol interval [ms]'] / 1000   # Waiting time between Symbols
        self.startTime = time.time()                                            # Get current system time
        self.binaryOrder = 0                                                    # Only for testing (symbol  number)
        self.timeNextInjection = 0                                              # Set slots for sending next Injection
        super().setup()

        """
        Initialisierung der Mikropumpe
        Aufgaben: 
        - Automatische Suche und Einstellung des richtigen Geräts (port)
        - Übernahme der Anfangsparameter von Spannung, Frequenz, Kanal, Modulation, Symbolinterval
        - Ermittelt aktuelle Systemlaufzeit für die Genauigkeit
        """

    def encode(self, sequence):

        symbol_values = []                                                      # Create list for symbols
        list4csk = []                                                           # Create list for 4-CSK
        list8csk = []                                                           # Create list for 8-CSK
        sequenceindecimal = [ord(i) for i in sequence]                          # Change sequence in decimal (ascii)
        sequencein8bit = [format(i, "08b") for i in sequenceindecimal]          # Change decimal in 8bit sequence


        """
           Informationskodierung in das Binärsystem.
           Aufgaben: 
           - Erstellung jeweilige Binärliste für 4-CSK und 8-CSK
           - Umwandlung von Zeichen in Dezimalzahlen (ascii)
           - Umwandlung von Dezimalzahlen in Binärsequenz (ascii)
           Bsp: A --> 65 --> 01000001 bzw. 
        """

        for x in range(len(sequencein8bit)):
            binary8index = [int(a) for a in str(sequencein8bit[x])]             # Change 8bit sequence in single Bits

            for i in range(len(binary8index)):
                if self.modulation == "OOK":                                    # 1Bit --> 1Symbol
                    if i % 8 == 0:
                        continue
                    symbol_values.append(str(binary8index[i]))

                if self.modulation == "4-CSK":                                  # 2Bit --> 1Symbol
                    list4csk.append(str(binary8index[i]))
                    if i % 2 == 1:
                        symbol_values.append(str((list4csk[i - 1]) + (list4csk[i])))

                if self.modulation == "8-CSK":                              # 3Bit --> 1Symbol
                    list8csk.append(str(binary8index[i]))
                    if i % 3 == 1 and i > 1:
                        symbol_values.append(str((list8csk[i - 2]) + (list8csk[i - 1]) + (list8csk[i])))
            list4csk.clear()
            list8csk.clear()
            # symbol_values.append("-") #Wenn du nach jedem Zeichen ein ein "-" willst, dann einfach das # entfernen
        symbol_values.append("-") # Behebt den Fehler, dass am noch Etwas gesendet wird. Danke Dir! :-)

        """
           Modulation der Kodierung.
           Aufgaben: 
           - Zusammenfassung von Binärsequenz in Symbole nach jeweiliger Modulation
           Bsp: OOK:    01000001    --> 0,1,0,0,0,0,0,1
                4-CSK:  01000001    --> 01,00,00,01
                8-CSK:  000001      --> 000,001 (weniger Zeichen kodierbar)
        """

        if self.modulation == "manually":  # Add two Bits to symbol list
            symbol_values.clear()
            symbol_values.append(sequence)

        if sequence == "500Symbole":
            symbol_values.clear()
            for i in range(500):
                i += 1
                symbol_values.append(0)
                symbol_values.append(1)
            symbol_values.append("-")
        if sequence == "100Symbole":
            symbol_values.clear()
            for i in range(100):
                i += 1
                symbol_values.append(0)
                symbol_values.append(1)
            symbol_values.append("-")
        if sequence == "10Symbole":
            symbol_values.clear()
            for i in range(10):
                i += 1
                symbol_values.append(0)
                symbol_values.append(1)
            symbol_values.append("-")

        """
           Individuelle Kodierung.
           Aufgaben: 
            - Vorgefertige Kodierungsschemen
        """

        self.timeNextInjection = 1                                              # Restart slots for sending
        self.bartels.micropump_set_frequency(self.frequency)
        self.startTime = time.time()                                             # Restart system time
        return symbol_values

    """
    Vorbereitung Transmit
    Aufgaben: 
    - Setzt Zeit für erste Injektion
    - Stellt Frequenz ein
    - Übernimmt aktuelle Systemzeit
    """

    def parameters_edited(self):

        self.channel = self.parameter_values['channel']
        self.frequency = self.parameter_values['frequency [Hz]']
        self.voltage = self.parameter_values['voltage [V]']
        # self.sleep_time = self.parameter_values['character interval [s]']
        self.port = self.parameter_values['port']
        self.modulation = self.parameter_values['modulation']
        self.symbolInterval = self.parameter_values['symbol interval [ms]'] / 1000

        """
        Aktualisierung Parameter
        Aufgaben: 
        - Prüft Parameter während der Laufzeit
        - Aktualisiert Parameter für die nächsten Übetragungen (außer Frequenz)
        """

    def transmit_single_symbol_value(self, symbol_value):
        print(time.time() - self.startTime)
        while (time.time() - self.startTime) < self.timeNextInjection:         # ... system time waits until nextsymbol
            pass

        if symbol_value != " -":                                                # If the Symbol 0 or 1 then ...
            timing = time.time() - self.startTime  # - self.timeNextInjection
            # print(timing)

            if self.modulation == "OOK":
                # print(str(self.binaryOrder) + ". gesendet: " + str(symbol_value) + "  " + str(timing))  # Testing
                self.bartels.micropump_set_voltage(self.channel, int(symbol_value) * self.voltage)
                self.timeNextInjection = self.timeNextInjection + self.symbolInterval
                # print(str(self.timer) + ". gesendet: " + str(symbol_value) + "  " + str(time.time() - self.timezero - timing))
                self.binaryOrder = (self.binaryOrder + 1) % 7  # Testing

            elif self.modulation == "4-CSK":
                if self.symbolInterval < 250:
                    self.symbolInterval = 0.250
                self.bartels.modulation_4CSK(self.channel, symbol_value, self.startTime, self.timeNextInjection)
                self.timeNextInjection = self.timeNextInjection + self.symbolInterval
                print(str(self.binaryOrder) + ". gesendet: " + str(symbol_value) + "  " + str(timing))

            elif self.modulation == "8-CSK":
                if self.symbolInterval < 500:
                    self.symbolInterval = 0.500
                self.bartels.modulation_8CSK(self.channel, symbol_value, self.startTime, self.timeNextInjection)
                self.timeNextInjection = self.timeNextInjection + self.symbolInterval
                print(str(self.binaryOrder) + ". gesendet: " + str(symbol_value) + "  " + str(timing))

                # MANUALLY #                                                            # only for testing
            elif self.modulation == "manually":
                self.bartels.manually(self.channel, self.voltage,  self.frequency, symbol_value)
                self.timeNextInjection = self.timeNextInjection + self.symbolInterval
                self.binaryOrder = (self.binaryOrder + 1) % 4
                print(str(self.binaryOrder) + ". gesendet: " + str(symbol_value) + "  " + str(time.time() - self.startTime))

        else:  # If Symbol "-" ...
            self.bartels.micropump_set_voltage(self.channel, 0)
            # self.timeNextInjection = self.timeNextInjection + self.symbolInterval

        self.timeNextInjection = round(self.timeNextInjection, 3)

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
            'default': BartelsTransmitter.micropump_find_ports(self=True),
            'max_length': 5,
        },

        {
            'description': "modulation",
            'dtype': 'item',
            'default': "OOK",
            'items': ["manually", "OOK", "4-CSK", "8-CSK"],
        },

        {
            'description': "channel",
            'dtype': 'item',
            'default': "1",
            'items': ["1", "2", "3", "4"],
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
            'max': 850,
        },

        # {
        #     'description': "character interval [s]",
        #     'decimals': 1,
        #     'dtype': 'int',
        #     'min': 100,
        #     'max': 100,
        #     'default': 0,
        # },

        {
            'description': "symbol interval [ms]",
            'decimals': 0,
            'dtype': 'float',
            'min': 0,
            'max': 10000,
            'default': 100,
        }

    ]

    """"
            Parameterauswahl
            Aufgaben: 
            - Gibt Parameterauswahl an
            - Begrenzung einzelner Parameter
    """
    return parameters
