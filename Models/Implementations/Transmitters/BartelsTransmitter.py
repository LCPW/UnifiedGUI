
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

    stopped = False

    def __init__(self, port):
        """
        Initialization of the Transmitter
        - select Highdriver
        - switch channels off
        """
        super().__init__()

        self.num_channels = 4
        self.channel_names = ["CH" + str(i) for i in range(self.num_channels)]
        self.channel_active = [False for i in range(self.num_channels)]

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

    def get_channel_active(self):
        """
        returns a bool array of length = channel amount, which indicates whether a certain channel is active or not.
        """
        return self.channel_active

    def shutdown(self):
        self.micropump_set_state(False)

        self.smp.close()

    def micropump_set_state(self, on):
        if on:
            BartelsTransmitter.stopped = False
            self.smp.write(b"PON\r\n")
            self.smp.readline().decode("ascii")
        else:
            self.micropump_disable_voltages()

            BartelsTransmitter.stopped = True
            self.smp.write(b"POFF\r\n")
            self.smp.readline().decode("ascii")
            self.smp.write(b"PA000#000#000#000\r\n")
            self.smp.readline().decode("ascii")
            time.sleep(0.1)
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

    def micropump_set_voltage(self, channel1, channel2, channel3, channel4, voltage):
        """
        Activation of the Bartels micropumps for a certain time duration.
        NOTE: This is a blocking function call and will stop the program for at least duration_ms!
        :param channel1: (bool) activate channel 1
        :param channel2: (bool) activate channel 2
        :param channel3: (bool) activate channel 3
        :param channel4: (bool) activate channel 4
        :param voltage: (int) 0-250
        """
        if BartelsTransmitter.stopped:
            return
        if voltage < 0 or voltage > 250:
            return

        voltages = [int(channel1)*voltage, int(channel2)*voltage, int(channel3)*voltage, int(channel4)*voltage]
        self.micropump_set_all_voltages(voltages)

        self.channel_active = voltages

    def micropump_disable_voltages(self):
        self.micropump_set_voltage(True, True, True, True, 0)
        self.channel_active = [False, False, False, False]

    def micropump_set_voltages_with_delay(self, on_voltages, off_voltages, delays, duration_ms):
        if duration_ms == 0:
            return
        
        #make lists of all points in time where pump changes occur
        on_times = delays
        off_times = [x+duration_ms for x in delays]

        #get sorted indices of events
        events = np.argsort(on_times + off_times)

        #start with base state
        voltages = [off_voltages]
        times = [0]

        for i in range(len(events)):
            event_pos = events[i]
            setting = voltages[-1].copy()
            if event_pos < 4:
                #this is an on event
                setting[event_pos] = on_voltages[event_pos]
                voltages.append(setting)

                times.append(delays[event_pos])
            else:
                #this is an off event
                event_pos = event_pos-4 #offset for off times
                setting[event_pos] = off_voltages[event_pos]
                voltages.append(setting)

                times.append(delays[event_pos] + duration_ms)

        #reverse lists so we can find the last unique value
        voltages.reverse()
        times.reverse()

        sorted_unique, indexes = np.unique(times, return_index=True)
        unique_voltages = [voltages[x] for x in sorted(indexes)]
        unique_times = [times[x] for x in sorted(indexes)]

        unique_voltages.reverse()
        unique_times.reverse()

        diff_times = np.diff(unique_times).tolist()

        #set initial state immediately
        if BartelsTransmitter.stopped:
                return
        self.micropump_set_all_voltages(unique_voltages[0])

        for n in range(len(diff_times)):
            time.sleep(diff_times[n]/1000)
            if BartelsTransmitter.stopped:
                return
            self.micropump_set_all_voltages(unique_voltages[n+1])

    def micropump_set_frequency(self, frequency):
        """
        set micropump voltage + duration
            parameters:
            frequency (int):  0-850
        """
        self.smp.write(b"F" + str.encode(str(frequency)) + b"\r\n")
