import numpy as np
import threading
import time, datetime

from Utils import Logging

LOOP_DELAY_MS = 10

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
        self.sleep_time = 1000 #ms
        self.transmission_canceled = False
        self.transmitters = None

    def setup(self):
        """
        Performs some further initialization.
        """

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

    def prepare_transmission(self, symbol_values):
        """
        Allow the encoder to setup any parameters relevant to the actual transmission
        This may be overriden in your implementation.
        """
        pass

    def clean_up_transmission(self):
        """
        Allow the encoder to spin down any parameters relevant to the actual transmission
        This may be overriden in your implementation.
        """
        pass

    def shutdown(self):
        self.cancel_transmission()

        while self.info['transmitting'] == True:
            time.sleep(LOOP_DELAY_MS)

        for tx in self.transmitters:
            tx.shutdown()

    def run_transmit_symbol_values(self, symbol_values):
        """
        Transmits a list of symbol values.
        :param symbol_values: List of symbol values.
        """

        self.prepare_transmission([int(val) for val in symbol_values])

        # Uniform sleep times
        if isinstance(self.sleep_time, float) or isinstance(self.sleep_time, int):
            transmission_time_offsets = [self.sleep_time] * (len(symbol_values)-1)
        # Non-uniform sleep times
        elif isinstance(self.sleep_time, list):
            if len(self.sleep_time) > len(symbol_values):
                transmission_time_offsets = self.sleep_time[:len(symbol_values)]
            elif len(self.sleep_time) < len(symbol_values):
                q, r = divmod(len(symbol_values), len(self.sleep_time))
                transmission_time_offsets = q * self.sleep_time + self.sleep_time[:r]
            else:
                transmission_time_offsets = self.sleep_time
        # Sleep time not well defined
        else:
            Logging.warning("sleep_time is neither a float nor a list, check your implementation.")
            transmission_time_offsets = [1000] * len(symbol_values)

        transmission_time_offsets.insert(0, 500) #start with 500ms delay
        transmission_times_offsets_acc = [sum(transmission_time_offsets[:y]) for y in range(1, len(transmission_time_offsets) + 1)]
        start_time = time.time()
        transmission_times = [x/1000 + start_time for x in transmission_times_offsets_acc]

        start_timestamp = datetime.datetime.fromtimestamp(transmission_times[0]).strftime(r"%H:%M:%S.%f")[:-3]
        end_timestamp = datetime.datetime.fromtimestamp(transmission_times[-1]).strftime(r"%H:%M:%S.%f")[:-3]
        Logging.info(f"First symbol at {start_timestamp}, last symbol at {end_timestamp}.")

        symbol_time = time.time()

        self.info['transmitting'] = True
        for sequence_index in range(len(symbol_values)):

            if time.time() > transmission_times[sequence_index]:
                Logging.warning("Timing error! Transmission time was hit before I was ready.")
                self.info['transmission_progress'] = int(np.round(((sequence_index + 1) / len(symbol_values)) * 100))
                continue

            while time.time() < transmission_times[sequence_index]:
                time.sleep(LOOP_DELAY_MS/1000)
                if self.transmission_canceled:
                    break

            if self.transmission_canceled:
                self.info['transmission_progress'] = 0
                self.transmission_canceled = False
                break

            symbol_time = time.time()
            self.transmit_single_symbol_value(int(symbol_values[sequence_index]))
            self.info['transmission_progress'] = int(np.round(((sequence_index + 1) / len(symbol_values)) * 100))

        time_offset = symbol_time*1000-transmission_times[-1]*1000
        symbol_timestamp = datetime.datetime.fromtimestamp(symbol_time).strftime(r"%H:%M:%S.%f")[:-3]
        Logging.info(f"Transmitted last symbol at {symbol_timestamp} (offset: {np.round(time_offset, 2)}ms).")


        self.clean_up_transmission()
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