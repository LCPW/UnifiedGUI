from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
import pyqtgraph as pg
import json
import os

from Utils import Logging

SETTINGS_PATH = os.path.join('Utils', 'PlotSettings', 'DecoderPlotSettings')


class PlotSettings:
    """
    Plot settings such as which datalines are shown, the color of the datalines or whether the symbol intervals
    are shown can be selected by the user during the execution of the program and are saved once the program is
    closed so they can be restored during the next execution (on the same device).
    """
    def __init__(self, decoder_info):
        """
        Initializes the plot settings.
        :param decoder_info: Information about decoder.
        """

        self.path = os.path.join(SETTINGS_PATH, 'plot_settings_' + decoder_info['type'] + '.json')

        try:
            with open(self.path, 'r') as s:
                self.settings = json.load(s)
        except IOError:
            Logging.info(f"No plot settings found for {decoder_info['type']}. Loading default settings.")
            self.load_default_settings(decoder_info)

    def load_default_settings(self, decoder_info):
        """
        Loads default settings which they user might have provided in the decoder implementation.
        If no information has been provided for a key, use a standard value.
        This is executed if the program is for the first time on a new device or the user clicked on the
        'Default settings' button in the plot settings dialog.
        :param decoder_info: Information about decoder.
        """
        receiver_info, landmark_info, plot_settings = decoder_info['receivers'], decoder_info['landmarks'], decoder_info['plot_settings']
        settings = {}

        if 'datalines_active' in list(plot_settings.keys()):
            settings['datalines_active'] = plot_settings['datalines_active']
        else:
            settings['datalines_active'] = []
            for receiver_index in range(receiver_info['num']):
                sensor_names = receiver_info['sensor_names'][receiver_index]
                settings['datalines_active'].append([True] * len(sensor_names))

        if 'datalines_color' in list(plot_settings.keys()):
            settings['datalines_color'] = plot_settings['datalines_color']
        else:
            settings['datalines_color'] = []
            current_color = 0
            for receiver_index in range(receiver_info['num']):
                sensor_names = receiver_info['sensor_names'][receiver_index]
                colors_ = []
                for sensor in sensor_names:
                    colors_.append(pg.intColor(current_color).name())
                    current_color += 1
                settings['datalines_color'].append(colors_)

        if 'datalines_style' in list(plot_settings.keys()):
            settings['datalines_style'] = plot_settings['datalines_style']
        else:
            settings['datalines_style'] = []
            for receiver_index in range(receiver_info['num']):
                sensor_names = receiver_info['sensor_names'][receiver_index]
                settings['datalines_style'].append(['SolidLine'] * len(sensor_names))

        if 'datalines_width' in list(plot_settings.keys()):
            settings['datalines_width'] = plot_settings['datalines_width']
        else:
            settings['datalines_width'] = 1

        if 'landmarks_active' in list(plot_settings.keys()):
            settings['landmarks_active'] = plot_settings['landmarks_active']
        else:
            settings['landmarks_active'] = [True] * landmark_info['num']

        if 'landmarks_color' in list(plot_settings.keys()):
            settings['landmarks_color'] = plot_settings['datalines_color']
        else:
            settings['landmarks_color'] = ['k'] * landmark_info['num']

        if 'landmarks_size' in list(plot_settings.keys()):
            settings['landmarks_size'] = plot_settings['landmarks_size']
        else:
            settings['landmarks_size'] = 15

        if 'landmarks_symbols' in list(plot_settings.keys()):
            settings['landmarks_symbols'] = plot_settings['landmarks_symbols']
        else:
            settings['landmarks_symbols'] = ['o'] * landmark_info['num']

        if 'step_size' in list(plot_settings.keys()):
            settings['step_size'] = plot_settings['step_size']
        else:
            settings['step_size'] = 1

        if 'symbol_intervals' in list(plot_settings.keys()):
            settings['symbol_intervals'] = plot_settings['symbol_intervals']
        else:
            settings['symbol_intervals'] = True

        if 'symbol_intervals_color' in list(plot_settings.keys()):
            settings['symbol_intervals_color'] = plot_settings['symbol_intervals_color']
        else:
            settings['symbol_intervals_color'] = 'k'

        if 'symbol_intervals_width' in list(plot_settings.keys()):
            settings['symbol_intervals_width'] = plot_settings['symbol_intervals_width']
        else:
            settings['symbol_intervals_width'] = 1

        if 'symbol_values' in list(plot_settings.keys()):
            settings['symbol_values'] = plot_settings['symbol_values']
        else:
            settings['symbol_values'] = True

        if 'symbol_values_fixed_height' in list(plot_settings.keys()):
            settings['symbol_values_fixed_height'] = plot_settings['symbol_values_fixed_height']
        else:
            settings['symbol_values_fixed_height'] = 1

        if 'symbol_values_height_factor' in list(plot_settings.keys()):
            settings['symbol_values_height_factor'] = plot_settings['symbol_values_height_factor']
        else:
            settings['symbol_values_height_factor'] = 1.1

        if 'symbol_values_position' in list(plot_settings.keys()):
            settings['symbol_values_position'] = plot_settings['symbol_values_position']
        else:
            settings['symbol_values_position'] = 'Above'

        if 'symbol_values_size' in list(plot_settings.keys()):
            settings['symbol_values_size'] = plot_settings['symbol_values_size']
        else:
            settings['symbol_values_size'] = 20

        self.settings = settings

    def save(self):
        """
        Saves the settings back to a JSON file.
        """
        if self.settings is not None:
            with open(self.path, 'w') as outfile:
                json.dump(self.settings, outfile, indent=4)
            self.settings = None