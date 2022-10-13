"""
Author: Benjamin Schiller
E-mail: benjamin.bs.schiller@fau.de
"""

# Install 'pyserial' for module 'serial'
import serial
import crcmod.predefined
import binascii

from Models.Interfaces.ReceiverInterface import ReceiverInterface


crc8 = crcmod.predefined.mkCrcFun('crc-8')
DATA_MSB = ['00', '02', '04', '06']
DATA_LSB = ['01', '03', '05', '07']
OFFSET = ['0C', '0D', '0E', '0F']
CLOCK_DIVIDERS = ['14', '15', '16', '17']
CLK_IN = 40 * 1000 * 1000


LDC1614_DEVICE_ID = '7F'
LDC1614_CONFIG = '1A'
LDC1614_MUX_CONFIG = '1B'


class LDC1614EVMReceiver(ReceiverInterface):
    """
    Decoder for the Texas Instruments LDC1614 Evaluation Module.
    Datasheet: https://www.ti.com/lit/ds/symlink/ldc1612.pdf
    """
    def __init__(self):
        super().__init__()

        self.num_sensors = 4
        self.sensor_names = ["Sensor CH" + str(i) + " (Hz)"for i in range(self.num_sensors)]
        self.channel = None
        self.drop_first_measurements = 5

        super().setup()

        self.serial_port = serial.Serial(port='COM3', baudrate=115200)
        device_id = read_reg(self.serial_port, LDC1614_DEVICE_ID)

        write_reg(self.serial_port, LDC1614_CONFIG, '0200')
        write_reg(self.serial_port, LDC1614_MUX_CONFIG, 'C20F')
        write_reg(self.serial_port, LDC1614_CONFIG, '0000')

    def listen_step(self):
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
        data_lsb = read_reg(self.serial_port, DATA_LSB[channel])
        data_msb = read_reg(self.serial_port, DATA_MSB[channel])

        # Convert to binary, drop the leading b' and fill up with leading zeros if necessary
        data_lsb = (bin(int(data_lsb, 16))[2:]).zfill(16)
        data_msb = (bin(int(data_msb, 16))[2:]).zfill(16)

        # Drop the leading 4 bits of the MSB because these are error bits and not part of the actual data
        data_msb = data_msb[4:]

        # Combine values from MSB and LSB to final value after converting them to integers
        data = int(data_msb, 2) * 2 ** 16 + int(data_lsb, 2)

        # Read offset register and convert to integer
        offset = read_reg(self.serial_port, OFFSET[channel])
        offset = (int(offset, 16))

        # Read clock dividers register, convert to bits, drop the leading b' and fill up with leading zeros if necessary
        clock_dividers = read_reg(self.serial_port, CLOCK_DIVIDERS[channel])
        clock_dividers = (bin(int(clock_dividers, 16))[2:]).zfill(16)

        # The first 10 bits represent the channel reference divider, the last 4 bits represent the channel input divider
        reference_divider = int(clock_dividers[:10], 2)
        input_divider = int(clock_dividers[12:], 2)

        # Calculate reference frequency and channel offset
        reference_frequency = CLK_IN / reference_divider
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
        print("Error in write register")


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
        print("Error in set register")
    serial_string = '4C140100022A02'
    serial_bytes = bytes.fromhex(serial_string)
    crc_byte = bytes([crc8(serial_bytes)])
    serial_port.write(serial_bytes + crc_byte)
    s = serial_port.read(32)
    if s[3] != 0:
        print("Error in read register")
    data_read = (str(hex(s[6]))[2:]).zfill(2) + (str(hex(s[7]))[2:]).zfill(2)
    return data_read