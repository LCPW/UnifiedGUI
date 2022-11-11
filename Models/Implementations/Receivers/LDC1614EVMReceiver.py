"""
Author: Benjamin Schiller
E-mail: benjamin.bs.schiller@fau.de
"""
import sys

# Install 'pyserial' for module 'serial'
import serial
import crcmod.predefined
import binascii

from Models.Interfaces.ReceiverInterface import ReceiverInterface
from Utils import Logging


crc8 = crcmod.predefined.mkCrcFun('crc-8')
DATA_MSB = ['00', '02', '04', '06']
DATA_LSB = ['01', '03', '05', '07']
OFFSET = ['0C', '0D', '0E', '0F']
CLOCK_DIVIDER = ['14', '15', '16', '17']
SETTLE_COUNT = ['10', '11', '12', '13']
REFERENCE_COUNT = ['08', '09', '0A', '0B']
DRIVE_CURRENT = ['1E', '1F', '20', '21']


DEVICE_ID = '7F'
CONFIG = '1A'
MUX_CONFIG = '1B'
STATUS = '18'


class LDC1614EVMReceiver(ReceiverInterface):
    """
    Decoder for the Texas Instruments LDC1614 Evaluation Module.
    Datasheet: https://www.ti.com/lit/ds/symlink/ldc1612.pdf
    """
    def __init__(self, num_channels, clk_in_mhz, com_port, deglitch_filter, settle_counts, reference_counts, low_power_activation_mode, drive_currents):
        super().__init__()

        self.num_sensors = num_channels
        self.clk_in_mhz = clk_in_mhz
        self.sensor_names = ["Sensor CH" + str(i) + " (MHz)" for i in range(self.num_sensors)]
        self.drop_first_measurements = 5

        super().setup()

        self.serial_port = serial.Serial(port='COM' + str(com_port), baudrate=115200)
        device_id = read_reg(self.serial_port, DEVICE_ID)
        Logging.info(f"Connected to LDC1614 with device ID 0x{device_id}.")

        if deglitch_filter == "1.0":
            deglitch_filter_bits = '001'
        elif deglitch_filter == "3.3":
            deglitch_filter_bits = '100'
        elif deglitch_filter == "10":
            deglitch_filter_bits = '101'
        else:
            deglitch_filter_bits = '111'

        mux_config_bits = '1100001000001' + deglitch_filter_bits
        # Enable/disable Rp override for sensor current drive
        use_drive_current = False if all(i == -1 for i in drive_currents) else True
        # Use reference frequency from CLKIN pin (6th bit)
        config_bits = '000' + ('1' if use_drive_current else '0') + ('1' if low_power_activation_mode else '0') + '01000000000'
        if use_drive_current:
            for s in range(self.num_sensors):
                drive_current_bits = bin(drive_currents[s])[2:].zfill(5) + '00000000000'
                write_reg(self.serial_port, DRIVE_CURRENT[s], binary_to_hex(drive_current_bits))

        write_reg(self.serial_port, CONFIG, binary_to_hex(config_bits))
        write_reg(self.serial_port, MUX_CONFIG, binary_to_hex(mux_config_bits))
        for s in range(self.num_sensors):
            write_reg(self.serial_port, SETTLE_COUNT[s], binary_to_hex(bin(settle_counts[s])[2:]))
            write_reg(self.serial_port, REFERENCE_COUNT[s], binary_to_hex(bin(reference_counts[s])[2:]))

    def listen_step(self):
        """
        Check if data ready flag is set (all channels have an unread conversion) and then read new values.
        """
        status = hex_to_binary(read_reg(self.serial_port, STATUS))
        data_ready = status[9]
        if data_ready == '1':
            values = []
            for i in range(self.num_sensors):
                frequency = self.get_frequency(i)
                values.append(frequency)
            self.append_values(values)

    def get_frequency(self, channel):
        """
        Reads the data registers and calculates the frequency for a given channel.
        :param channel: Channel to be read.
        :return: Frequency (Hz).
        """
        # Read least and most significant bytes register (2 each)
        data_lsb = hex_to_binary(read_reg(self.serial_port, DATA_LSB[channel]))
        data_msb = hex_to_binary(read_reg(self.serial_port, DATA_MSB[channel]))

        # Drop the leading 4 bits of the MSB because these are error bits and not part of the actual data
        error_bits = data_msb[:4]
        if error_bits[0] != '0':
            Logging.warning(f"ERR_UR{channel}: Channel {channel} Conversion Under-range Error")
        if error_bits[1] != '0':
            Logging.warning(f"ERR_OR{channel}: Channel {channel} Conversion Over-range Error")
        if error_bits[2] != '0':
            Logging.warning(f"ERR_WD{channel}: Channel {channel} Conversion Watchdog Timeout Error")
        if error_bits[3] != '0':
            Logging.warning(f"ERR_AE{channel}: Channel {channel} Conversion Amplitude Error")
        data_msb = data_msb[4:]

        # Combine values from MSB and LSB to final value after converting them to integers
        data = int(data_msb, 2) * 2 ** 16 + int(data_lsb, 2)

        # Read offset register and convert to integer
        offset = read_reg(self.serial_port, OFFSET[channel])
        offset = (int(offset, 16))

        # Read clock dividers register, convert to bits, drop the leading b' and fill up with leading zeros if necessary
        clock_dividers = read_reg(self.serial_port, CLOCK_DIVIDER[channel])
        clock_dividers = (bin(int(clock_dividers, 16))[2:]).zfill(16)

        # The first 10 bits represent the channel reference divider, the last 4 bits represent the channel input divider
        reference_divider = int(clock_dividers[6:], 2)
        input_divider = int(clock_dividers[:4], 2)

        # Calculate reference frequency and channel offset
        reference_frequency = self.clk_in_mhz / reference_divider
        channel_offset = (offset / 2 ** 16) * reference_frequency

        # Calculate frequency (see page 39 of the data sheet)
        frequency = input_divider * reference_frequency * ((data / 2 ** 28) + (channel_offset / 2 ** 16))

        return frequency


def write_reg(serial_port, addr, data):
    """
    Writes on the serial connection
    :param serial_port: Serial port.
    :param addr: Address.
    :param data: Data.
    """
    serial_string = '4C150100042A' + addr + data
    serial_bytes = bytes.fromhex(serial_string)
    crc_byte = bytes([crc8(serial_bytes)])
    serial_port.write(serial_bytes + crc_byte)
    s = serial_port.read(32)
    if s[3] != 0:
        Logging.warning("Error in write register")


def read_reg(serial_port, addr):
    """
    Reads from the serial connection.
    :param serial_port: Serial port.
    :param addr: Address.
    :return: Read data (2 bytes) in hex representation.
    """
    serial_string = '4C150100022A' + addr
    serial_bytes = bytes.fromhex(serial_string)
    crc_byte = bytes([crc8(serial_bytes)])
    serial_port.write(serial_bytes + crc_byte)
    s = serial_port.read(32)
    if s[3] != 0:
        Logging.warning("Error in set register")
    serial_string = '4C140100022A02'
    serial_bytes = bytes.fromhex(serial_string)
    crc_byte = bytes([crc8(serial_bytes)])
    serial_port.write(serial_bytes + crc_byte)
    s = serial_port.read(32)
    if s[3] != 0:
        Logging.warning("Error in set register")
    data_read = (str(hex(s[6]))[2:]).zfill(2) + (str(hex(s[7]))[2:]).zfill(2)
    return data_read


def binary_to_hex(binary):
    """
    Converts a binary string to 4-symbol hex value.
    :param binary: Binary string.
    :return: Hex value.
    """
    return (hex(int(binary, 2))[2:]).zfill(4)


def hex_to_binary(hex_string):
    """
    Converts hex number to binary (16-bit).
    Convert to binary, drop the leading b' and fill up with leading zeros if necessary
    :param hex_string: Hex string.
    :return: Binary string.
    """
    return (bin(int(hex_string, 16))[2:]).zfill(16)