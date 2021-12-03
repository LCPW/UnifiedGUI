import shelve
import json
import os

SETTINGS_PATH = os.path.join('.', 'Utils', 'Settings')


class Settings:
    def __init__(self):
        #self.settings = None
        #self.default_settings = None
        self.path = os.path.join(SETTINGS_PATH, 'settings.json')
        self.default_path = os.path.join(SETTINGS_PATH, 'settings_default.json')

        with open(self.default_path, 'r') as s:
            self.settings_default = json.load(s)

        try:
            with open(self.path, 'r') as s:
                self.settings = json.load(s)
        except IOError:
            # TODO: Feedback
            self.settings = self.settings_default

        # TODO: Check completeness
        for key in list(self.settings_default.keys()):
            if key not in (list(self.settings.keys())):
                self.settings[key] = self.settings_default[key]

        #self.close_()

    # TODO: Destructor?
    def close_(self):
        with open(self.path, 'w') as outfile:
            json.dump(self.settings, outfile, indent=4)

    def get(self, key):
        pass

# class PlotSettings:
#     def __init__(self):
#         self.plot_settings = shelve.open(os.path.join(SETTINGS_PATH, 'plot_settings'))
#
#     def close(self):
#         self.plot_settings.close()
#
#     def get(self, key):
#         return self.plot_settings[key]
#
#     def set(self, key, value):
#         self.plot_settings[key] = value