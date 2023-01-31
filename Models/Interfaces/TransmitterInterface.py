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
        pass

    def shutdown(self):
        #Allow for any closing stuff
        pass