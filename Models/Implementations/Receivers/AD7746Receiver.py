

from Models.Interfaces.ReceiverInterface import ReceiverInterface
from Utils import Logging

import serial
import time

class AD7746Receiver(ReceiverInterface):

    HARDWARE_ID = "2341:8037" #Arduino Micro
    #HARDWARE_ID = "2341:0043" #Arduino Uno
    DEVICE_ID = "MacMolComCapacitiveSensor"
    BAUDRATE = 115200
    TIMEOUT = 0.2 #s

    def __init__(self, port, conversion_time_level, excitation_level, active_channel, channel_diff):
        super().__init__()

        self.num_sensors = 1
        self.sensor_names = ["Capacitance"]

        self.smp = serial.Serial()
        self.smp.port = str(port)
        self.smp.baudrate = AD7746Receiver.BAUDRATE
        self.smp.timeout = AD7746Receiver.TIMEOUT
        if not self.smp.is_open:
            try:
                self.smp.open()
            except serial.serialutil.SerialException:
                Logging.error("Cannot connect to selected port.")
                return

        self.smp.write(str.encode("ID\r\n"))
        read_id = self.smp.readline().decode('utf-8').replace("\r\n", "")
        if read_id != AD7746Receiver.DEVICE_ID:
            Logging.warning("Unexpected device ID. Are you sure you are connected to the correct port?")

        self.set_conversion_time(conversion_time_level)
        self.set_excitation_level(excitation_level)
        self.set_channel_config(active_channel, channel_diff)

        self.ms_offset = None
        self.start_rx_time = None

        super().setup()

    def set_conversion_time(self, time_level):
        #"T0\r\n", 0 = 11.0ms; 1=11.9ms; 2=20.0ms; 3=38.0ms; 4=62.0ms; 5=77.0ms; 6=92.0ms; 7=109.6ms  

        self.smp.write(b"T" + str.encode(str(time_level)) + b"\r\n")
        self.smp.readline()

    def set_excitation_level(self, excitation_level):
        #"E3\r\n", 0 = Vdd/8, 1 = Vdd/4, 2 =Vdd3/8, 3 = Vdd/2

        self.smp.write(b"E" + str.encode(str(excitation_level)) + b"\r\n")
        self.smp.readline()

    def set_channel_config(self, active_channel, channel_diff):
        #"C11\r\n", first digit 1/2 = Channel 1/2, second digit 0/1 = differential mode off/on

        ch_diff_val = 1 if channel_diff else 0
        
        self.smp.write(b"C" + str.encode(str(active_channel)) + str.encode(str(ch_diff_val)) + b"\r\n")
        self.smp.readline()

    def set_status(self, on):
        write_cmd = b"STOP"
        if on:
            write_cmd = b"START"
            
            #Reset times for this transmission
            self.ms_offset = None
            self.start_rx_time = None

        self.smp.write(write_cmd + b"\r\n")
        self.smp.readline()
        
    def convert_raw_value(self, raw_value):
        #Data is 0x000000 - 0xFFFFFF with 0x800000=0
        #max value is +4.096pF, min value is -4.096pF

        zero_corrected = raw_value - 8388608
        out_val = zero_corrected*4096/8388607 #fF
        return out_val

    def convert_timestamp(self, uc_time):
        #uc_time is ms since the uc startup (will loop after about 40days)

        if self.ms_offset == None:
            #Set initial offset
            self.ms_offset = uc_time
            self.start_rx_time = time.time()
        
        timestamp = (uc_time-self.ms_offset)/1000 + self.start_rx_time
        return timestamp


    def shutdown(self):
        self.set_status(False)
        self.smp.close()


    def listen_step(self):
        
        if self.smp.in_waiting > 0:
            dataset = self.smp.readline().decode("ascii")
            elements = dataset.split(", ")
            if len(elements) != 2:
                Logging.warning("Unexpected receiver message: " + dataset)
                return

            try:
                uc_time = int(elements[0])
                raw_value = int(elements[1])
                self.append_values([self.convert_raw_value(raw_value)], self.convert_timestamp(uc_time))
            except:
                Logging.warning("Unexpected receiver message.")