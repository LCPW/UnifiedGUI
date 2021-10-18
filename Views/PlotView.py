from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
import pyqtgraph as pg

from Views import PlotWidgetView, PlotSettingsDialog


class PlotView(QWidget):
    def __init__(self):
        super().__init__()

        self.settings = {
            'legend': True,
            'active': [],
            'pens': []
        }

        layout = QVBoxLayout()

        self.plot_settings_dialog = PlotSettingsDialog.PlotSettingsDialog(self)
        self.plot_widget = PlotWidgetView.PlotWidgetView(self)

        self.toolbar = QToolBar()
        self.button_settings = QToolButton()
        self.button_settings.setText("Settings")
        self.button_settings.clicked.connect(self.show_settings)
        self.toolbar.addWidget(self.button_settings)

        layout.addWidget(self.toolbar)
        layout.addWidget(self.plot_widget)
        self.setLayout(layout)

        self.current_color = 0

    def set_style(self, i, j):
        # Qt.SolidLine, etc.
        qstyle = getattr(Qt, self.plot_settings_dialog.comboboxes_style[i][j].currentText())
        self.settings['pens'][i][j].setStyle(qstyle)
        self.plot_widget.update_pens(i, j)

    def set_color(self, i, j):
        color = QColorDialog.getColor()
        # print(color)
        self.settings['pens'][i][j].setColor(color)
        self.plot_widget.update_pens(i, j)
        self.plot_settings_dialog.buttons_color[i][j].setStyleSheet("background-color: " + self.settings['pens'][i][j].color().name())

    def set_width(self, i, j):
        # TODO: Get width
        width = 2
        self.settings['pens'][i][j].setWidth(width)
        self.plot_widget.update_pens(i, j)

    def add_datalines(self, receiver_info):
        for i in range(len(receiver_info)):
            sensor_descriptions = receiver_info[i]['sensor_descriptions']
            active_ = []
            pens_ = []
            for j in range(len(sensor_descriptions)):
                active_.append(True)
                #pens_.append(pg.mkPen(color=pg.intColor(self.current_color), width=2, style=Qt.SolidLine))
                pens_.append(pg.mkPen(color=pg.intColor(self.current_color), style=Qt.SolidLine))
                self.current_color += 1
            self.settings['active'].append(active_)
            self.settings['pens'].append(pens_)

        self.plot_widget.add_datalines(receiver_info)
        self.plot_settings_dialog.add_receivers(receiver_info)

    def remove_datalines(self):
        self.plot_widget.remove_datalines()
        # TODO: Settings Menu
        self.current_color = 0

    def update_values(self, vals):
        self.plot_widget.update_values(vals)

    def toggle_checkbox(self, receiver_index, sensor_index):
        current_state = self.settings['active'][receiver_index][sensor_index]
        self.settings['active'][receiver_index][sensor_index] = not current_state

        all_, any_ = all(self.settings['active'][receiver_index]), any(self.settings['active'][receiver_index])
        state = 2 if all_ else (1 if any_ else 0)

        self.plot_settings_dialog.checkboxes_receivers_active[receiver_index].setCheckState(Qt.CheckState(state))

    def set_all(self, receiver_index, state):
        for sensor_index in range(len(self.settings['active'][receiver_index])):
            self.settings['active'][receiver_index][sensor_index] = state

    def toggle_receiver_checkbox(self, receiver_index):
        state = self.plot_settings_dialog.checkboxes_receivers_active[receiver_index].checkState()
        if state == 0:
            self.plot_settings_dialog.set_receiver_checkboxes(receiver_index, False)
            self.set_all(receiver_index, False)
        else:
            state = 2
            self.plot_settings_dialog.checkboxes_receivers_active[receiver_index].setCheckState(Qt.CheckState(state))
            self.plot_settings_dialog.set_receiver_checkboxes(receiver_index, True)
            self.set_all(receiver_index, True)

    def show_settings(self):
        # TODO: Fokus auf Dialog, wenn nochmal geklickt
        self.plot_settings_dialog.show()