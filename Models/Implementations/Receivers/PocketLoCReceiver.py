

from Models.Interfaces.ReceiverInterface import ReceiverInterface
from Utils import Logging

import serial
import time
import re

class PocketLoCReceiver(ReceiverInterface):

    HARDWARE_ID = "2341:8037"
    DEVICE_ID = "PocketLoCSensor"
    BAUDRATE = 115200
    TIMEOUT = 0.1 #s

    def __init__(self, port, active_sensor_channels):
        super().__init__()

        self.num_sensors = len(active_sensor_channels)*2
        self.sensor_names = ["1-" + x for x in active_sensor_channels] + ["2-" + x for x in active_sensor_channels]

        self.smp = serial.Serial()
        self.smp.port = str(port)
        self.smp.baudrate = PocketLoCReceiver.BAUDRATE
        self.smp.timeout = PocketLoCReceiver.TIMEOUT
        if not self.smp.is_open:
            try:
                self.smp.open()
            except serial.serialutil.SerialException:
                Logging.error("Cannot connect to selected port.")
                return

        self.smp.write(str.encode("ID\r\n"))
        read_id = self.smp.readline().decode('utf-8').replace("\r\n", "")
        if read_id != PocketLoCReceiver.DEVICE_ID:
            Logging.warning("Unexpected device ID. Are you sure you are connected to the correct port?")

        self.set_mux(active_sensor_channels)

        global error_flag
        error_flag = False

        super().setup()

    def send_command(self, command):
        #send a command on the active serial connection
        
        byte_cmd = str.encode(command + "\r\n")
        self.smp.write(byte_cmd)

    def read_response(self, n):
        # Get n lines of data from the serial connection and strip line terminator
        for i in range(n):
            raw = self.smp.readline().decode('utf-8')
            Logging.info(raw.replace("\r\n", ""))

    def set_gain(self, gain_level):
        # Gain level can be 0...10
        gain_cmd = "G" + str(gain_level)
        self.send_command(gain_cmd)
        self.read_response(1)

    def set_mux(self, active_list):
        #Try to create the mux command for the sensor depending on a string array of actviated photodiodes
        #Max. 6 photodiodes can be activated at once
        #Accepted string inputs are F1, F2, F3, F4, F5, F6, F7, F8, CLEAR, NIR
        
        diode_names = ["F1", "F2", "F3", "F4", "F5", "F6", "F7", "F8", "CLEAR", "NIR"]
        
        output_mux = [0] * 10
        
        for diode in active_list:
            try:
                idx = diode_names.index(diode)
                output_mux[idx] = 1
            except ValueError:
                Logging.error("The specified photodiode does not exist. Check your config. Results may contain unexpected values.")
        
        if sum(output_mux) > 6:
            Logging.error("You have selected to many photodiodes. Check your config. Only the first 6 diodes will actually be set.")
        
        command = "C" + "".join(str(x) for x in output_mux)

        self.send_command(command)
        self.read_response(3)

    def set_sample_time(self, sample_duration):
        # sample duration in ms - good values are 5~10ms
        time_command = "T" + str(sample_duration)
        self.send_command(time_command)
        self.read_response(1)

    def read_values(self):
        # Get a line of data from the serial connection and parse it
        raw = self.smp.read(188).decode('utf-8')
        raw_items = re.split(",", raw)
        
        sensor0_vals = [0,0,0,0,0,0]
        sensor1_vals = [0,0,0,0,0,0]
        saturation_error = False
        timestamp = time.time()
        
        try:
            values = [float(x) for x in raw_items[0:14]]
            sensor0_vals = values[0:6]
            sensor1_vals = values[7:13]
            saturation_error = values[6] > 0 or values[13] > 0
        except Exception:
            Logging.warning("Error parsing values:")
            Logging.warning(raw)
            return None, None, None, None
        
        global error_flag
        
        if saturation_error:
            #Saturation error - only report if new
            if not error_flag:
                error_flag = True
                Logging.warning("Sensor saturation error! You should probably reduce the gain.")
        else:
            error_flag = False

        
        return sensor0_vals, sensor1_vals, saturation_error, timestamp

    
    def set_status(self, on):
        write_cmd = "STOP"
        if on:
            write_cmd = "START"

        self.send_command(write_cmd)
        self.read_response(1)
        
    def shutdown(self):
        self.set_status(False)
        self.smp.close()


    def listen_step(self):
        
        while self.smp.in_waiting >= 188:
            sensor0, sensor1, sat_err, timestamp = self.read_values()
            if sensor0 is None:
                return

            self.append_values(sensor0 + sensor1, timestamp)