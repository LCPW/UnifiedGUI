

from Models.Interfaces.ReceiverInterface import ReceiverInterface
from Utils import Logging

import serial
import time

class IntegratedReceiver(ReceiverInterface):

    HARDWARE_ID = "2341:8037" #Arduino Micro
    #HARDWARE_ID = "2341:0043" #Arduino Uno
    DEVICE_ID = "MacMolComIntegratedSensor"
    BAUDRATE = 115200
    TIMEOUT = 0.2 #s

    def __init__(self, port, 
                 cap_conversion_time_level, cap_excitation_level, cap_active_channel, cap_channel_diff, 
                 ind_num_channels, ind_clk_in_mhz, ind_deglitch_filter, ind_settle_count, ind_reference_count):
        super().__init__()

        self.num_sensors = 3
        self.sensor_names = ["Capacitance", "Inductance Ch0", "Inductance Ch1"]

        self.smp = serial.Serial()
        self.smp.port = str(port)
        self.smp.baudrate = IntegratedReceiver.BAUDRATE
        self.smp.timeout = IntegratedReceiver.TIMEOUT
        if not self.smp.is_open:
            try:
                self.smp.open()
            except serial.serialutil.SerialException:
                Logging.error("Cannot connect to selected port.")
                return

        self.smp.write(str.encode("ID\r\n"))
        read_id = self.smp.readline().decode('utf-8').replace("\r\n", "")
        if read_id != IntegratedReceiver.DEVICE_ID:
            Logging.warning("Unexpected device ID. Are you sure you are connected to the correct port?")

        self.set_cap_conversion_time(cap_conversion_time_level)
        self.set_cap_excitation_level(cap_excitation_level)
        self.set_cap_channel_config(cap_active_channel, cap_channel_diff)

        self.set_ind_mux_config(ind_deglitch_filter, ind_num_channels)
        self.set_ind_settle_count(ind_settle_count)
        self.set_ind_reference_count(ind_reference_count)

        self.ms_offset = None
        self.start_rx_time = None

        super().setup()

    def set_cap_conversion_time(self, time_level):
        #"T0\r\n", 0 = 11.0ms; 1=11.9ms; 2=20.0ms; 3=38.0ms; 4=62.0ms; 5=77.0ms; 6=92.0ms; 7=109.6ms  

        self.smp.write(b"T" + str.encode(str(time_level)) + b"\r\n")
        self.smp.readline()

    def set_cap_excitation_level(self, excitation_level):
        #"E3\r\n", 0 = Vdd/8, 1 = Vdd/4, 2 =Vdd3/8, 3 = Vdd/2

        self.smp.write(b"E" + str.encode(str(excitation_level)) + b"\r\n")
        self.smp.readline()

    def set_cap_channel_config(self, active_channel, channel_diff):
        #"C11\r\n", first digit 1/2 = Channel 1/2, second digit 0/1 = differential mode off/on

        ch_diff_val = 1 if channel_diff else 0
        
        self.smp.write(b"C" + str.encode(str(active_channel)) + str.encode(str(ch_diff_val)) + b"\r\n")
        self.smp.readline()

    def set_ind_mux_config(self, deglitch_filter_value, channel_count):
        filter_set = 0
        if deglitch_filter_value == "1.0":
            filter_set = 0b001
        elif deglitch_filter_value == "3.3":
            filter_set = 0b100
        elif deglitch_filter_value == "10":
            filter_set = 0b101
        else:
            filter_set = 0b111

        self.smp.write(b"D" + str.encode(str(filter_set)) + b"\r\n")
        self.smp.readline()

        self.smp.write(b"M" + str.encode(str(channel_count)) + b"\r\n")
        self.smp.readline()


    def set_ind_settle_count(self, settle_count):
        self.smp.write(b"S" + str.encode(str(settle_count)) + b"\r\n")
        self.smp.readline()

    def set_ind_reference_count(self, r_count):
        self.smp.write(b"R" + str.encode(str(r_count)) + b"\r\n")
        self.smp.readline()

    def set_active_devices(self, cap_active, ind_active):
        cap_set = 0
        ind_set = 0
        if cap_active:
            cap_set = 1
        if ind_active:
            ind_set = 1

        self.smp.write(b"X" + str.encode(str(cap_set)) + str.encode(str(ind_set)) + b"\r\n")
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
        
    def convert_raw_cap_value(self, raw_value):
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
            if len(elements) != 5:
                Logging.warning("Unexpected receiver message: " + dataset)
                return

            uc_time = int(elements[0])
            raw_cap_value = int(elements[1])
            raw_ind0_value = int(elements[2])
            raw_ind1_value = int(elements[3])
            ind_channel_errors = int(elements[4])
            self.append_values([self.convert_raw_cap_value(raw_cap_value)], self.convert_timestamp(uc_time))