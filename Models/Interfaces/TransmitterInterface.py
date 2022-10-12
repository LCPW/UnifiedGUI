import time

from Utils import Logging
from Utils.Settings import SettingsStore


class TransmitterInterface:
    """
    A transmitter is used to control the input to a communication channel.
    For instance, a transmitter may regulate the pressure of a pump or
    the amount of background flow in the case of fluids.
    """
    def __init__(self):
        self.sleep_time = 0.01

    def transmit(self):
        """
        Runs an infinite loop of calling transmit_step after a certain interval.
        """
        while True:
            self.transmit_step()
            time.sleep(self.sleep_time)

    def transmit_step(self):
        """
        Transmission step called periodically.
        Should be overriden in the concrete transmitter implementation.
        """
        Logging.warning("transmit_step not implemented in your transmitter!")