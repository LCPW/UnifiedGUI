"""
Author: Steve Kungu
E-mail: steve.kungu@fau.de
"""

import time
import serial.tools.list_ports
import serial
import numpy as np
from Utils import Logging

from Models.Interfaces.TransmitterInterface import TransmitterInterface


class BartelsTransmitter(TransmitterInterface):

    HARDWARE_ID = "2341:8037"
    DEVICE_ID = "PocketLoCPumpController"
    BAUDRATE = 9600
    TIMEOUT = 0.1 #s

    def __init__(self, port):
        """
        Initialization of the Transmitter
        - select Highdriver
        - switch channels off
        """
        super().__init__()

        self.smp = serial.Serial()
        self.smp.port = str(port)
        self.smp.baudrate = BartelsTransmitter.BAUDRATE
        self.smp.timeout = BartelsTransmitter.TIMEOUT
        if not self.smp.is_open:
            try:
                self.smp.open()
            except serial.serialutil.SerialException:
                Logging.error("Cannot connect to selected port.")
                return

        self.smp.write(str.encode("ID\r\n"))
        read_id = self.smp.readline().decode('utf-8').replace("\r\n", "")
        if read_id != BartelsTransmitter.DEVICE_ID:
            Logging.warning("Unexpected device ID. Are you sure you are connected to the correct port?")

        self.smp.write(b"SELECTQUADDRIVER\r\n")
        self.smp.readline().decode("ascii")
        self.micropump_set_state(False)

    def shutdown(self):
        self.micropump_set_state(False)

        self.smp.close()

    def micropump_set_state(self, on):
        if on:
            self.smp.write(b"PON\r\n")
            self.smp.readline().decode("ascii")
        else:
            self.smp.write(b"POFF\r\n")
            self.smp.readline().decode("ascii")
            self.smp.write(b"PA000#000#000#000\r\n")
            self.smp.readline().decode("ascii")
        

    def micropump_set_all_voltages(self, channel_voltages):

        # PA<aaa>#<bbb>#<ccc>#<ddd>
        # Set the voltage of all four pumps (<aaa> for pump 1, <bbb> for pump 2, ...). Each value must be zero-padded to exactly three characters.
        command = "PA{:03d}#{:03d}#{:03d}#{:03d}\r\n".format(channel_voltages[0], channel_voltages[1], channel_voltages[2], channel_voltages[3])

        self.smp.write(str.encode(command))
        self.smp.readline().decode("ascii")

    def micropump_set_voltage_duration(self, channel1, channel2, channel3, channel4, voltage, duration_ms):
        """
        set micropump frequency
            parameters:
            channel (int):  1-4
            voltage (int):  0-250
            duration (int): 0-10000
        """

        channels = [int(channel1), int(channel2), int(channel3), int(channel4)]
        self.micropump_set_all_voltages_duration(self, channels*voltage, [0,0,0,0], duration_ms)


    def micropump_set_all_voltages_duration(self, on_voltages, off_voltages, duration_ms):
        if duration_ms == 0:
            return
        
        self.micropump_set_all_voltages(on_voltages)
        time.sleep(duration_ms/1000)

        self.micropump_set_all_voltages(off_voltages)

    def micropump_set_voltages_with_delay(self, on_voltages, off_voltages, delays, duration_ms):
        if duration_ms == 0:
            return
        
        #make lists of all points in time where pump changes occur
        on_times = delays
        off_times = delays+duration_ms

        #get sorted indices of events
        events = np.argsort(on_times + off_times)

        #start with base state
        voltages = [off_voltages]
        times = [0]

        time_sum = 0

        for i in len(events):
            event_pos = events.index(i)
            setting = voltages[-1]
            if event_pos < 4:
                #this is an on event
                setting[event_pos] = on_voltages[event_pos]
                voltages.append(setting)

                diff_time = delays[event_pos] - time_sum
                time_sum = delays[event_pos]
                times.append(diff_time)
            else:
                #this is an off event
                event_pos = event_pos-4 #offset for off times
                setting[event_pos] = off_voltages[event_pos]
                voltages.append(setting)

                diff_time = delays[event_pos] + duration_ms - time_sum
                time_sum = delays[event_pos] + duration_ms
                times.append(diff_time)

        #reverse lists so we can find the last unique value
        voltages.reverse()
        times.reverse()

        unique_times, indexes = np.unique(times, return_index=True)
        unique_voltages = voltages[indexes]

        unique_times.reverse()
        unique_voltages.reverse()

        for n in len(unique_times):
            time.sleep(unique_times[n]/1000)
            self.micropump_set_all_voltages(unique_voltages[n])


    def micropump_set_frequency(self, frequency):
        """
        set micropump voltage + duration
            parameters:
            frequency (int):  0-850
        """
        self.smp.write(b"F" + str.encode(str(frequency)) + b"\r\n")

