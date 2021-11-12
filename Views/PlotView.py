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
            'pens': [],
            'landmarks_active': [],
            'landmarks_symbols': [],
            'symbol_intervals': True,
            'symbol_intervals_pen': pg.mkPen(color='k', width=1),
            'symbol_values': True,
        }

        # TODO: Refactor
        self.symbols = {
            'Circle': 'o',
            'Square': 's',
            'Diamond': 'd',
            'Plus': '+',
            'Triangle pointing downwards': 't',
            'Triangle pointing upwards': 't1',
            'Triangle pointing right side': 't2',
            'Triangle pointing left side': 't3',
            'Pentagon': 'p',
            'Hexagon': 'h',
            'Star': 'star',
            'Cross': 'x',
            #'Arrow up': 'arrow_up',
            #'Arrow down': 'arrow_down',
            #'Arrow left': 'arrow_left',
            #'Crosshair': 'crosshair'
        }

        layout = QVBoxLayout()

        self.plot_settings_dialog = PlotSettingsDialog.PlotSettingsDialog(self)
        self.plot_widget = PlotWidgetView.PlotWidgetView(self)

        self.toolbar = QToolBar()
        self.button_settings = QToolButton()
        self.button_settings.setText("Settings")
        self.button_settings.setIcon(QIcon('./Views/Icons/settings.png'))
        self.button_settings.setEnabled(False)
        self.button_settings.clicked.connect(self.show_settings)
        self.toolbar.addWidget(self.button_settings)

        layout.addWidget(self.toolbar)
        layout.addWidget(self.plot_widget)
        self.setLayout(layout)

        self.current_color = 0

    def decoder_added(self, receiver_info, landmark_info):
        self.add_datalines(receiver_info)
        self.add_landmarks(landmark_info)

    def set_style(self, i, j):
        # Qt.SolidLine, etc.
        qstyle = getattr(Qt, self.plot_settings_dialog.comboboxes_style[i][j].currentText())
        self.settings['pens'][i][j].setStyle(qstyle)
        self.plot_widget.update_pens(i, j)

    def set_color(self, i, j):
        color = QColorDialog.getColor()
        # Is False if the user pressed Cancel
        if color.isValid():
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
                # pens_.append(pg.mkPen(color=pg.intColor(self.current_color), width=2, style=Qt.SolidLine))
                pens_.append(pg.mkPen(color=pg.intColor(self.current_color), style=Qt.SolidLine))
                self.current_color += 1
            self.settings['active'].append(active_)
            self.settings['pens'].append(pens_)

        self.plot_widget.add_datalines(receiver_info)
        self.plot_settings_dialog.add_datalines(receiver_info)
        self.button_settings.setEnabled(True)

    def decoder_removed(self):
        self.plot_widget.remove_datalines()
        self.plot_settings_dialog.remove_datalines()
        self.button_settings.setEnabled(False)
        self.settings['active'] = []
        self.settings['pens'] = []
        self.current_color = 0

    def add_landmarks(self, landmark_info):
        num_landmarks = landmark_info['num']
        for i in range(num_landmarks):
            self.settings['landmarks_active'].append(True)
            self.settings['landmarks_symbols'].append(landmark_info['symbols'][i])
        self.plot_widget.add_landmarks(landmark_info)
        self.plot_settings_dialog.add_landmarks(landmark_info)

    def update_landmarks(self, landmarks):
        self.plot_widget.update_landmarks(landmarks)

    def toggle_all_landmarks(self):
        state = self.plot_settings_dialog.checkbox_all_landmarks.checkState()
        if state == 0:
            self.plot_settings_dialog.set_landmark_checkboxes(False)
            self.set_all_landmarks(False)
        else:
            state = 2
            self.plot_settings_dialog.checkbox_all_landmarks.setCheckState(Qt.CheckState(state))
            self.plot_settings_dialog.set_landmark_checkboxes(True)
            self.set_all_landmarks(True)

    def toggle_landmark(self, landmark_index):
        state = self.plot_settings_dialog.checkboxes_landmarks[landmark_index].checkState()
        self.settings['landmarks_active'][landmark_index] = state
        if state:
            self.plot_widget.activate_landmarks(landmark_index)
        else:
            self.plot_widget.deactivate_landmarks(landmark_index)

        all_, any_ = all(self.settings['landmarks_active']), any(self.settings['landmarks_active'])
        state = 2 if all_ else (1 if any_ else 0)

        self.plot_settings_dialog.checkbox_all_landmarks.setCheckState(Qt.CheckState(state))

    def set_all_landmarks(self, state):
        for landmark_index in range(len(self.settings['landmarks_active'])):
            self.settings['landmarks_active'][landmark_index] = state
            if state:
                self.plot_widget.activate_landmarks(landmark_index)
            else:
                self.plot_widget.deactivate_landmarks(landmark_index)

    def set_landmark_symbol(self, landmark_index):
        symbol = self.symbols[self.plot_settings_dialog.comboboxes_landmarks_symbol[landmark_index].currentText()]
        self.settings['landmarks_symbols'][landmark_index] = symbol
        self.plot_widget.update_landmarks_symbols(landmark_index)

    def update_values(self, vals):
        self.plot_widget.update_values(vals)

    def update_symbol_intervals(self, symbol_intervals):
        self.plot_widget.update_symbol_intervals(symbol_intervals)

    def update_symbol_values(self, symbol_intervals, symbol_values):
        self.plot_widget.update_symbol_values(symbol_intervals, symbol_values)

    def toggle_checkbox(self, receiver_index, sensor_index):
        current_state = self.settings['active'][receiver_index][sensor_index]
        self.settings['active'][receiver_index][sensor_index] = not current_state
        # True -> False
        if current_state:
            self.plot_widget.deactivate_dataline(receiver_index, sensor_index)
        # False -> True
        else:
            self.plot_widget.activate_dataline(receiver_index, sensor_index)

        all_, any_ = all(self.settings['active'][receiver_index]), any(self.settings['active'][receiver_index])
        state = 2 if all_ else (1 if any_ else 0)

        self.plot_settings_dialog.checkboxes_receivers_active[receiver_index].setCheckState(Qt.CheckState(state))

    def set_all_datalines(self, receiver_index, state):
        """
        Sets all datalines of a given receiver to a given state.
        @param receiver_index: Index of the receiver.
        @param state: New state of the datalines.
        """
        for sensor_index in range(len(self.settings['active'][receiver_index])):
            self.settings['active'][receiver_index][sensor_index] = state
            if state:
                self.plot_widget.activate_dataline(receiver_index, sensor_index)
            else:
                self.plot_widget.deactivate_dataline(receiver_index, sensor_index)

    def toggle_receiver_checkbox(self, receiver_index):
        state = self.plot_settings_dialog.checkboxes_receivers_active[receiver_index].checkState()
        if state == 0:
            self.plot_settings_dialog.set_receiver_checkboxes(receiver_index, False)
            self.set_all_datalines(receiver_index, False)
        else:
            state = 2
            self.plot_settings_dialog.checkboxes_receivers_active[receiver_index].setCheckState(Qt.CheckState(state))
            self.plot_settings_dialog.set_receiver_checkboxes(receiver_index, True)
            self.set_all_datalines(receiver_index, True)

    def toggle_symbol_intervals(self):
        state = self.plot_settings_dialog.checkbox_symbol_intervals.checkState()
        self.settings['symbol_intervals'] = state
        if state:
            self.plot_widget.activate_symbol_intervals()
        else:
            self.plot_widget.deactivate_symbol_intervals()

    def toggle_symbol_values(self):
        state = self.plot_settings_dialog.checkbox_symbol_values.checkState()
        self.settings['symbol_values'] = state
        if state:
            self.plot_widget.activate_symbol_values()
        else:
            self.plot_widget.deactivate_symbol_values()

    def show_settings(self):
        self.plot_settings_dialog.show()
        # Set this as the active window
        self.plot_settings_dialog.activateWindow()