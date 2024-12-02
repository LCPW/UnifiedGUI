# Install 'pyserial' for module 'serial'
import serial
import crcmod.predefined

from Models.Interfaces.ReceiverInterface import ReceiverInterface
from Utils import Logging

import struct

crc8 = crcmod.predefined.mkCrcFun('crc-8')
# LDC1614 EVM registers
DATA_MSB = ['00', '02', '04', '06']
DATA_LSB = ['01', '03', '05', '07']
OFFSET = ['0C', '0D', '0E', '0F']
CLOCK_DIVIDER = ['14', '15', '16', '17']
SETTLE_COUNT = ['10', '11', '12', '13']
REFERENCE_COUNT = ['08', '09', '0A', '0B']
DRIVE_CURRENT = ['1E', '1F', '20', '21']

DEVICE_ID = '7F'
CONFIG = '1A'
ERROR_CONFIG = '19'
MUX_CONFIG = '1B'
STATUS = '18'

# FAQ on serial com with LDC16xx EVM
# https://e2e.ti.com/support/sensors-group/sensors/f/sensors-forum/295036/faq-inductive-sensing-faq---frequently-asked-questions#Q40

WRITE_REG_COMMAND = "4C150100042A"  # syntax HEADER XX YYYY ZZ, XX write reg adress, YYYY two bytes to write MSB first, ZZ CRC-8 check sum
# after write, MCU responds with 32 bytes - byte 4 is zero if command is correct

SET_REG_COMMAND = "4C150100022A"  # syntax HEADER XX ZZ, xx reg adress to read, ZZ CRC-8 check sum
# after set, MCU responds with 32 bytes - byte 4 is zero if command is correct

READ_REG_COMMAND = "4C140100022A02"  # syntax HEADER ZZ, ZZ CRC-8 check sum
# after read, MCU responds with 32 bytes - byte 4 is zero if command is correct, bytes 7 and 8 contain MSB and LSB of read

START_STREAMING_COMMAND = "4C0501000601290404302AC1"
# after set, MCU responds with 32 bytes - byte 4 is zero if command is correct
# will periodically output 32 bytes - bytes 7-10 CH0, bytes 11-14 CH1, ... MSB first

STOP_STREAMING_COMMAND = "4C0601000101D2"


# after set, MCU responds with 32 bytes - byte 4 is zero if command is correct


class LDC1614EVMReceiver(ReceiverInterface):
    """
    Decoder for the Texas Instruments LDC1614 Evaluation Module.
    Datasheet: https://www.ti.com/lit/ds/symlink/ldc1612.pdf
    """

    HARDWARE_ID = "2047:08F8"  # LDC1614 EVM
    BAUDRATE = 115200
    TIMEOUT = 0.1  # s

    def __init__(self, num_channels, clk_in_mhz, com_port, deglitch_filter, settle_count, reference_count):
        super().__init__()

        self.num_sensors = 4
        self.active_channels = num_channels
        self.clk_in_mhz = clk_in_mhz
        self.sensor_names = ["CH" + str(i) + " (MHz)" for i in range(4)]
        self.drop_first_measurements = 10

        super().setup()

        self.serial_port = serial.Serial()
        self.serial_port.port = com_port
        self.serial_port.baudrate = LDC1614EVMReceiver.BAUDRATE
        self.serial_port.timeout = LDC1614EVMReceiver.TIMEOUT
        if not self.serial_port.is_open:
            try:
                self.serial_port.open()
            except serial.serialutil.SerialException:
                Logging.error("Cannot connect to selected port.")
                return

        self.set_error_config()
        self.set_mux_config(deglitch_filter, num_channels)
        self.set_settle_count(settle_count)
        self.set_reference_count(reference_count)
        self.set_config()

    def set_mux_config(self, deglitch_filter_value, channel_count):
        filter_set = 0
        if deglitch_filter_value == "1.0":
            filter_set = 0b001
        elif deglitch_filter_value == "3.3":
            filter_set = 0b100
        elif deglitch_filter_value == "10":
            filter_set = 0b101
        else:
            filter_set = 0b111  # DATASHEET IS ambigous, either b011 or b111, experiments indicate that b111 is correct

        # We can set single channel or auto channel using CH0 & 1, CH0 & 1 & 2 or CH0 & 1 & 2 & 3
        autoscan_enable = 0
        rr_sequence = 0
        if channel_count > 1:
            autoscan_enable = 1
            rr_sequence = channel_count - 2

        mux_config = 0b0000001000001000
        mux_config |= autoscan_enable << 15
        mux_config |= rr_sequence << 13
        mux_config |= filter_set << 0

        self.write_register(MUX_CONFIG, f'{mux_config:04x}')

    def set_settle_count(self, settle_count):
        for ch in range(4):
            self.write_register(SETTLE_COUNT[ch], f'{settle_count:04x}')

    def set_reference_count(self, r_count):
        for ch in range(4):
            self.write_register(REFERENCE_COUNT[ch], f'{r_count:04x}')

    def set_config(self):
        # Default config
        config = 0b0000001000000001
        # CH0 when in single mode, sleep off, no I override, full current sensor activation
        # auto amplitude correction, external clk, res, use interrupt pin, normal current, resx6

        self.write_register(CONFIG, f'{config:04x}')

    def set_error_config(self):
        # Report errors to data fields and no error interrupts
        error_config = 0b1111100000000000

        self.write_register(ERROR_CONFIG, f'{error_config:04x}')

    def set_streaming(self, on):
        if on:
            self.send_command(START_STREAMING_COMMAND, False)
        else:
            self.send_command(STOP_STREAMING_COMMAND, False)

    def listen_step(self):
        """
        Check if data ready flag is set (all channels have an unread conversion) and then read new values.
        """

        if self.serial_port.in_waiting >= 32:
            ch0, ch1, ch2, ch3 = self.read_stream_line()

            values = [ch0]
            if self.active_channels > 1:
                values.append(ch1)
            if self.active_channels > 2:
                values.append(ch2)
            if self.active_channels > 3:
                values.append(ch3)

            self.append_values(values)

    def is_data_ready(self, channel):
        status = self.read_register(STATUS)
        return status & (1 << (3 - channel)) > 0

    def read_stream_line(self):
        read = self.serial_port.read(32)

        # see https://docs.python.org/3/library/struct.html#struct.calcsize
        # '>'=Big Endian, '3x' = 3 times pad byte (no value), 'B'=unsigned char, '2x'= 2 times pad byte, 'H'=unsigned short (2 bytes), '10x' = 10 times pad byte
        (error_code, ch0_msb, ch0_lsb, ch1_msb, ch1_lsb, ch2_msb, ch2_lsb, ch3_msb, ch3_lsb) = struct.unpack(
            '>3xB2xHHHHHHHH10x', read)
        if error_code:
            print('Error reported from serial.')
            ch0 = 0
            ch1 = 0
            ch2 = 0
            ch3 = 0
        else:
            ch0 = self.calculate_frequency(ch0_msb, ch0_lsb, 0)
            ch1 = self.calculate_frequency(ch1_msb, ch1_lsb, 1)
            ch2 = self.calculate_frequency(ch2_msb, ch2_lsb, 2)
            ch3 = self.calculate_frequency(ch3_msb, ch3_lsb, 3)

        return ch0, ch1, ch2, ch3

    def calculate_frequency(self, data_msb, data_lsb, channel):
        # The leading 4 bits of the MSB are error bits and not part of the actual data

        tes = data_msb & (1 << 15)
        if data_msb & (1 << 15) > 0 and channel < self.active_channels:
            Logging.warning(f"ERR_UR{channel}: Channel {channel} Conversion Under-range Error", repeat=False)
        if data_msb & (1 << 14) > 0 and channel < self.active_channels:
            Logging.warning(f"ERR_OR{channel}: Channel {channel} Conversion Over-range Error", repeat=False)
        if data_msb & (1 << 13) > 0 and channel < self.active_channels:
            Logging.warning(f"ERR_WD{channel}: Channel {channel} Conversion Watchdog Timeout Error", repeat=False)
        if data_msb & (1 << 12) > 0 and channel < self.active_channels:
            Logging.warning(f"ERR_AE{channel}: Channel {channel} Conversion Amplitude Error", repeat=False)

        # Clear error bits for value calculation
        data_msb &= 0b0000111111111111

        # Combine values from MSB and LSB to final value
        data = (data_msb << 16) + data_lsb

        # Calculate reference frequency and channel offset
        offset = 0  # we currently do not use an offset or dividers
        reference_divider = 1
        input_divider = 1
        reference_frequency = self.clk_in_mhz * 1000000 / reference_divider
        channel_offset = (
                                     offset / 2 ** 16) * reference_frequency  # TODO ERROR - OFFSET IS CALCULATED TWICE - SEE BELOW!

        # Calculate frequency (see page 39 of the data sheet)
        frequency = input_divider * reference_frequency * ((data / 2 ** 28) + (channel_offset / 2 ** 16))
        return frequency

    def get_channel_frequency(self, channel):
        """
        Reads the data registers and calculates the frequency for a given channel.
        :param channel: Channel to be read.
        :return: Frequency (Hz).
        """
        # Read most and least significant bytes register (2 each)
        data_msb = self.read_register(DATA_MSB[channel])
        data_lsb = self.read_register(DATA_LSB[channel])  # MUST BE READ AFTER MSB - to ensure data coherency!

        return self.calculate_frequency(data_msb, data_lsb, channel)

    def shutdown(self):
        self.serial_port.close()

    def send_command(self, command, append_crc=True):
        out_cmd = bytes.fromhex(command.upper())
        if append_crc:
            crc_byte = bytes([crc8(out_cmd)])
            out_cmd += crc_byte

        self.serial_port.write(out_cmd)
        response = self.serial_port.read(32)
        # byte 4 indicates an error
        if response[3] != 0:
            Logging.warning("Error setting command " + command)

        return response

    def write_register(self, register, data):
        self.send_command(WRITE_REG_COMMAND + register + data)

    def read_register(self, register):
        self.send_command(SET_REG_COMMAND + register)
        response = self.send_command(READ_REG_COMMAND)
        resp_msb = response[6]
        resp_lsb = response[7]

        val = (resp_msb << 16) + resp_lsb
        return val