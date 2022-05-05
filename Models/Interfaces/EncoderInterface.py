import numpy as np
import threading
import time

from Utils import Logging


class EncoderInterface:
    """
    An encoder consists of n transmitters.
    An encoder also provides an encoding scheme that transforms a sequence (e.g., a string)
    to symbol values that can then be transmitted.
    """
    def __init__(self, parameters, parameter_values):
        self.parameters = parameters
        self.parameter_values = parameter_values

        self.allowed_sequence_values = None
        self.allowed_symbol_values = None
        self.info = {
            'type': self.__class__.__name__,
            'transmission_progress': 0,
            'transmitting': False,
        }
        # Sleep time between individual symbols, should be overridden
        self.sleep_time = 1
        self.transmission_canceled = False
        self.transmitters = None

    def setup(self):
        """
        Performs some further initialization.
        """
        for transmitter in self.transmitters:
            thread = threading.Thread(target=transmitter.transmit, daemon=True)
            thread.start()

    def cancel_transmission(self):
        self.transmission_canceled = True

    def check_sequence(self, sequence):
        return self.allowed_sequence_values is None or all([s in self.allowed_sequence_values for s in sequence])

    def check_symbol_values(self, symbol_values):
        return self.allowed_symbol_values is None or all([s in self.allowed_symbol_values for s in symbol_values])

    def encode_with_check(self, sequence):
        if not self.check_sequence(sequence):
            Logging.warning("Sequence contains symbols that are not included in allowed symbols!", repeat=True)
            return ""
        else:
            return self.encode(sequence)

    def encode(self, sequence):
        """
        Encodes a sequence to a list of symbol values.
        Should be overridden in the concrete implementation.
        :param sequence: Sequence to be encoded.
        :return: Encoded sequence on success, else empty string.
        """
        Logging.warning("encode is not implemented in your encoder!", repeat=True)
        return ""

    def parameters_edited(self):
        """
        Do stuff when the parameters are edited by the user.
        May be overriden in the concrete implementation.
        """
        pass

    def run_transmit_symbol_values(self, symbol_values):
        """
        Transmits a list of symbol values.
        :param symbol_values: List of symbol values.
        """
        self.info['transmitting'] = True
        for sequence_index in range(len(symbol_values)):
            if self.transmission_canceled:
                self.info['transmission_progress'] = 0
                self.transmission_canceled = False
                break
            time_before = time.time()
            self.transmit_single_symbol_value(symbol_values[sequence_index])
            # More accurate
            time.sleep(self.sleep_time - (time_before - time.time()))
            self.info['transmission_progress'] = int(np.round(((sequence_index + 1) / len(symbol_values)) * 100))
        self.info['transmitting'] = False

    def transmit_single_symbol_value(self, symbol_value):
        """
        Transmits a single symbol value.
        Should be overridden in the concrete implementation.
        :param symbol_value: Symbol value to be transmitted.
        """
        Logging.warning("transmit_single_symbol not implemented in your encoder!", repeat=True)

    def transmit_symbol_values(self, symbol_values):
        """
        Transmits a list of symbol values.
        First checks whether the list contains only valid symbol values, then transmits the symbol values in a new thread.
        :param symbol_values: List of symbol values to be transmitted.
        """
        if not self.check_symbol_values(symbol_values):
            Logging.warning("Symbol values contains symbols that are not included in allowed symbol values!", repeat=True)
        else:
            thread = threading.Thread(target=self.run_transmit_symbol_values, args=(symbol_values,), daemon=True)
            thread.start()