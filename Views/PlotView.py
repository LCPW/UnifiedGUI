from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from Views import PlotWidgetView, PlotSettingsDialog


class PlotView(QWidget):
    def __init__(self):
        super().__init__()

        layout = QVBoxLayout()

        self.plot_settings_dialog = PlotSettingsDialog.PlotSettingsDialog(self)
        self.plot_widget = PlotWidgetView.PlotWidgetView()

        self.toolbar = QToolBar()
        self.button_settings = QToolButton()
        self.button_settings.setText("Settings")
        self.button_settings.clicked.connect(self.show_settings)
        self.toolbar.addWidget(self.button_settings)

        self.button_clear = QToolButton()
        self.button_clear.setText("Clear")
        self.button_clear.clicked.connect(self.plot_widget.clear)
        self.toolbar.addWidget(self.button_clear)

        layout.addWidget(self.toolbar)

        layout.addWidget(self.plot_widget)

        self.setLayout(layout)

        self.current_color = 0
        self.settings = {
            'legend': True,
            'receivers': []
        }

    def add_datalines(self, receiver_info):
        self.plot_widget.add_datalines(receiver_info)
        self.plot_settings_dialog.add_receivers(receiver_info)
        for i in range(len(receiver_info)):
            r = {
                # Tri-state?
                'active': True,
                'sensors': []
            }
            for j in range(len(receiver_info[i])):
                s = {
                    'active': True,
                    # Get color by int?
                    'color': self.plot_widget.get_color(self.current_color),
                    'thickness': 2,
                    'line': None
                }
                self.current_color += 1
                r['sensors'].append(s)
            self.settings['receivers'].append(r)

    def remove_datalines(self):
        self.plot_widget.remove_datalines()
        # TODO: Settings Menu
        self.current_color = 0

    def update_values(self, vals):
        self.plot_widget.update_values(vals)

    def show_settings(self):
        # if self.plot_settings_dialog.isVisible():
        #     self.plot_settings_dialog.hide()
        # else:
        #     self.plot_settings_dialog.show()

        self.plot_settings_dialog.show()