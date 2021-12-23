import shelve
import json
import os

from Utils import Logging

SETTINGS_PATH = os.path.join('Utils', 'Settings')

# TODO: Docu


class Settings:
    def __init__(self):
        self.path = os.path.join(SETTINGS_PATH, 'settings.json')
        self.default_path = os.path.join(SETTINGS_PATH, 'settings_default.json')

        with open(self.default_path, 'r') as s:
            self.settings_default = json.load(s)

        try:
            with open(self.path, 'r') as s:
                self.settings = json.load(s)
        except IOError:
            Logging.info("No settings file found, using default settings.")
            self.settings = self.settings_default

        # Check completeness
        for key in list(self.settings_default.keys()):
            if key not in (list(self.settings.keys())):
                self.settings[key] = self.settings_default[key]

    def shutdown(self):
        with open(self.path, 'w') as outfile:
            json.dump(self.settings, outfile, indent=4)

    def get(self, key):
        pass