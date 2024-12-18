import sys
import numpy as np
import threading
import time, datetime

from Utils import Logging
from Utils.Settings import SettingsStore

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

        # Sleep time between individual symbols, should be overridden
        self.sleep_time = 1000 #ms
        self.transmission_canceled = False
        self.num_transmitters = 0
        self.transmitters = None
        self.transmitter_names = None

        self.recording = False
        self.plot_settings = {}

        self.timestamps = []
        self.transmitted = []
        self.lengths = []
        self.min_timestamp = time.time()
        self.max_timestamp = time.time()

    def setup(self):
        """
        Performs some further initialization.
        """
        self.num_transmitters = len(self.transmitters)

        self.info = {
            'type': self.__class__.__name__,
            'transmission_progress': 0,
            'transmitting': False,
            'plot_settings': self.plot_settings,
            'transmitters': {
                'num': self.num_transmitters,
                'names': self.transmitter_names,
                'channel_names': []
            }
        }

        for transmitter_index in range(self.num_transmitters):
            self.timestamps.append(None)
            self.transmitted.append(None)
            self.lengths.append(0)
            self.info['transmitters']['channel_names'].append(self.transmitters[transmitter_index].channel_names)

    def append_transmission(self, transmitter_index, timestamp, values):
        """
        Appends a new timestamp for a given transmitter.
        :param transmitter_index: Transmitter index.
        :param timestamp: New timestamp.
        :param values: New measurement values.
        """
        dataset_length = self.lengths[transmitter_index]
        if dataset_length == 0:
            self.timestamps[transmitter_index] = np.empty((SettingsStore.settings['ENCODER_ARRAY_LENGTH'],))
            self.timestamps[transmitter_index][0] = timestamp
            self.transmitted[transmitter_index] = np.empty(
                (SettingsStore.settings['ENCODER_ARRAY_LENGTH'], len(values)))
            self.transmitted[transmitter_index][0] = np.array(values)
        else:
            if dataset_length == len(self.timestamps[transmitter_index]):  # maximum size reached -> allocate more
                self.timestamps[transmitter_index] = np.concatenate((self.timestamps[transmitter_index], np.empty(
                    (SettingsStore.settings['ENCODER_ARRAY_LENGTH'],))))
                self.transmitted[transmitter_index] = np.vstack((self.transmitted[transmitter_index], np.empty(
                    (SettingsStore.settings['ENCODER_ARRAY_LENGTH'], len(values)))))

            self.timestamps[transmitter_index][dataset_length] = timestamp
            self.transmitted[transmitter_index][dataset_length] = values

        self.lengths[transmitter_index] += 1

        min_timestamp = sys.float_info.max  # init with maximum value
        max_timestamp = 0  # init with minimum value
        for t_idx in range(len(self.timestamps)):
            if self.lengths[t_idx] > 0:
                min_tmp = np.min(self.timestamps[t_idx][:self.lengths[t_idx]])
                max_tmp = np.max(self.timestamps[t_idx][:self.lengths[t_idx]])
                if min_tmp < min_timestamp:
                    min_timestamp = min_tmp
                if max_tmp > max_timestamp:
                    max_timestamp = max_tmp

        now = time.time()
        self.min_timestamp = min(min_timestamp, now)
        self.max_timestamp = min(max_timestamp, now)

    def append_transmission_transmitter_values(self, timestamp, values):
        if self.recording:
            for transmitter_index in range(self.num_transmitters):
                self.append_transmission(transmitter_index, timestamp, values[transmitter_index])

    def cancel_transmission(self):
        self.transmission_canceled = True

    def check_sequence(self, sequence):
        return self.allowed_sequence_values is None or all([s in self.allowed_sequence_values for s in sequence])

    def check_symbol_values(self, symbol_values):
        return self.allowed_symbol_values is None or all([s in self.allowed_symbol_values for s in symbol_values])

    def clear_recording(self):
        """
        Clears all data from the encoder recording.
        """
        # Clear received
        self.lengths = [0] * self.num_transmitters
        self.transmitted = [None] * self.num_transmitters
        self.timestamps = [None] * self.num_transmitters

        self.min_timestamp = time.time()
        self.max_timestamp = time.time()

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

    def export_custom(self, workbook):
        """
        Exports transmitted data by creating a new table for every transmitter.
        :param workbook: .xlsx workbook object
        """
        bold = workbook.add_format({'bold': True})  # Add a bold format to use to highlight cells.

        # Gather data of the transmitters
        received = self.encoded['transmitted']
        lengths, timestamps, values = received['lengths'], received['timestamps'], received['values']
        # Iterate through all receivers to save single worksheets (one per transmitter)
        for transmitter_idx in range(self.num_transmitters):
            # Gather data of the next transmitter and create a new worksheet
            dataset_length = lengths[transmitter_idx]
            dataset_timestamp = timestamps[transmitter_idx]
            dataset_values = values[transmitter_idx]
            if dataset_values is None:
                continue

            worksheet = workbook.add_worksheet(self.transmitter_names[transmitter_idx])

            # Iterate through the value-pairs, usually one value array per channel present
            for value_idx in range(dataset_values.shape[1]):
                # Add headers for each time-value pair
                worksheet.write(0, 2*value_idx, "Time", bold)
                worksheet.write(0, 2*value_idx+1, self.transmitters[transmitter_idx].channel_names[value_idx], bold)

                # Add each row for the current time-value pair
                for row_idx in range(dataset_length):
                    worksheet.write(row_idx+1, 2*value_idx, dataset_timestamp[row_idx])
                    worksheet.write(row_idx+1, 2*value_idx+1, dataset_values[row_idx, value_idx])

    def get_transmitter_current_symbols(self):
        """
        Returns a list of currently transmitted symbols by the transmitters. (for example: active/inactive=1/0)
        :return: A list of symbols, with a length equal to the amount of transmitters present.
        """
        Logging.warning("get_transmitter_current_symbols is not implemented in your encoder!", repeat=True)
        return None

    def is_recording(self):
        """
        return true, when the encoder has been set to recording mode.
        """
        return self.recording

    def set_recording(self, active):
        """
        set the recording mode of the encoder.
        """
        self.recording = active

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

    def update_datalines(self):
        """
        This method will be periodically called by the controller.
        If no transmission is running, the data values needs to be updated with zero values to realise a smooth plot.
        """
        # Add zero data values
        symbol_time = time.time()
        transmitter_symbols = self.get_transmitter_current_symbols()
        if transmitter_symbols is None:
            return

        self.append_transmission_transmitter_values(symbol_time,transmitter_symbols)

    # TODO: this whole method seems a bit chaotic and the timing could be more precise.
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
                transmission_time_offsets = self.sleep_time[:len(symbol_values)-1]
            elif len(self.sleep_time) < len(symbol_values)-1:
                q, r = divmod(len(symbol_values), len(self.sleep_time))
                transmission_time_offsets = q * self.sleep_time + self.sleep_time[:r]
            else:
                transmission_time_offsets = self.sleep_time
        # Sleep time not well defined
        else:
            Logging.warning("sleep_time is neither a float nor a list, check your implementation.")
            transmission_time_offsets = [1000] * len(symbol_values)

        transmission_time_offsets.insert(0, 500) # start with 500ms delay
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

            while time.time() < transmission_times[sequence_index] and not self.transmission_canceled:
                time.sleep(LOOP_DELAY_MS/1000)

            if self.transmission_canceled:
                self.info['transmission_progress'] = 0
                self.transmission_canceled = False
                break

            symbol_time = time.time()
            self.transmit_single_symbol_value(int(symbol_values[sequence_index]))  # blocking call
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

    def get_encoded(self):
        """
        Returns current encoder values.
        :return: Current encoder values.
        """
        self.encoded = {
            'transmitted': {
                'lengths': self.lengths,
                'timestamps': self.timestamps,
                'values': self.transmitted
            },
            'min_timestamp': self.min_timestamp,
            'max_timestamp': self.max_timestamp
        }
        return self.encoded
