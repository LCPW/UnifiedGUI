import json
import os

from Utils import Logging

"""
This module allows for settings to be stored after closing the window.
"""

DIRECTORY = os.path.join('Utils', 'Settings')
SETTINGS_PATH = os.path.join(DIRECTORY, 'settings.json')
SETTINGS_DEFAULT_PATH = os.path.join(DIRECTORY, 'settings_default.json')

settings = None

with open(SETTINGS_DEFAULT_PATH, 'r') as s:
    settings_default = json.load(s)

try:
    with open(SETTINGS_PATH, 'r') as s:
        settings = json.load(s)
except IOError:
    Logging.info("No settings file found, using default settings.")
    settings = settings_default

# Check completeness
for key in list(settings_default.keys()):
    if key not in (list(settings.keys())):
        settings[key] = settings_default[key]


def shutdown():
    """
    Save settings in JSON file.
    """
    with open(SETTINGS_PATH, 'w') as outfile:
        json.dump(settings, outfile, indent=4)