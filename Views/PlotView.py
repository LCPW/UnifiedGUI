from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
import pyqtgraph as pg
import shelve

from Views import PlotWidgetView, PlotSettingsDialog, Utils
from Utils import Settings

# TODO: Refactor?
X_RANGE = {
    'decimals': 4,
    'min': 1e-4,
    'max': 100,
    'initial': 5
}

SYMBOLS = {
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
    'Crosshair': 'crosshair',
    # 'Arrow up': 'arrow_up',
    # 'Arrow down': 'arrow_down',
    # 'Arrow left': 'arrow_left'
}


class PlotView(QWidget):
    def __init__(self, data_view):
        super().__init__()

        # Important: datalines_width > 1 often causes lag!
        # TODO: Split pen
        self._settings = {
            'legend': True,
            'datalines_active': [],
            'datalines_width': 1,
            'datalines_color': [],
            'datalines_style': [],
            'datalines_pens': [],
            'landmarks_active': [],
            'landmarks_symbols': [],
            'symbol_intervals': True,
            'symbol_intervals_color': 'k',
            'symbol_intervals_width': 1,
            'symbol_intervals_pen': pg.mkPen(color='k', width=1),
            'symbol_values': True,
            'symbol_values_height_factor': 1.1
        }

        #self.s = Settings.PlotSettings()
        #for x in self._settings:
        #    self.s.set(x, self._settings[x])

        layout = QVBoxLayout()

        self.data_view = data_view
        self.plot_settings_dialog = PlotSettingsDialog.PlotSettingsDialog(self)
        self.plot_widget = PlotWidgetView.PlotWidgetView(self)

        self.toolbar = QToolBar()

        # X range settings
        self.label_range = QLabel("X-Axis Range[s]")
        self.button_range = QToolButton()
        self.button_range.setToolTip("Auto (no limit)")
        self.button_range.setIcon(QIcon('./Views/Icons/all_inclusive.png'))
        self.button_range.setEnabled(True)
        self.button_range.clicked.connect(lambda: self.set_x_range('button'))
        self.slider_range = QSlider(Qt.Horizontal)
        self.slider_range.setRange(max(X_RANGE['min'], 1), X_RANGE['max'])
        self.slider_range.setValue(X_RANGE['initial'])
        self.slider_range.sliderMoved.connect(lambda: self.set_x_range('slider'))
        self.spinbox_range = QDoubleSpinBox()
        self.spinbox_range.setDecimals(X_RANGE['decimals'])
        self.spinbox_range.setRange(X_RANGE['min'], X_RANGE['max'])
        self.spinbox_range.setValue(X_RANGE['initial'])
        self.spinbox_range.setSingleStep(1.0)
        self.spinbox_range.valueChanged.connect(lambda: self.set_x_range('spinbox'))
        # Actually set the x range
        self.plot_widget.plotItem.setLimits(maxXRange=X_RANGE['initial'])

        self.toolbar.addWidget(self.label_range)
        self.toolbar.addWidget(self.button_range)
        self.toolbar.addWidget(self.slider_range)
        self.toolbar.addWidget(self.spinbox_range)

        # Spacer widget
        empty = QWidget()
        empty.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        self.toolbar.addWidget(empty)

        # Plot settings button
        self.button_settings = QToolButton()
        self.button_settings.setToolTip("Settings")
        self.button_settings.setIcon(Utils.get_icon('settings'))
        self.button_settings.setEnabled(False)
        self.button_settings.clicked.connect(self.show_settings)
        self.toolbar.addWidget(self.button_settings)

        layout.addWidget(self.toolbar)
        layout.addWidget(self.plot_widget)
        self.setLayout(layout)

        self.current_color = 0

        # self._settings = shelve.open('plot_settings')

    @property
    def settings(self):
        # TODO: shelve
        return self._settings

    def add_datalines(self, receiver_info):
        """
        Adds new datalines.
        This function is usually executed when a new decoder has been added.
        :param receiver_info: Information about the receivers.
        """
        for i in range(len(receiver_info)):
            sensor_names = receiver_info[i]['sensor_names']
            active_ = []
            pens_ = []
            for j in range(len(sensor_names)):
                active_.append(True)
                pens_.append(pg.mkPen(color=pg.intColor(self.current_color), width=self.settings['datalines_width'], style=Qt.SolidLine))
                self.current_color += 1
            self.settings['datalines_active'].append(active_)
            self.settings['datalines_pens'].append(pens_)

        self.plot_widget.add_datalines(receiver_info)
        self.plot_settings_dialog.add_datalines(receiver_info)
        self.button_settings.setEnabled(True)

    def add_landmarks(self, landmark_info):
        """
        Adds new landmarks.
        This function is usually executed when a new decoder has been added.
        :param landmark_info: Information about the landmarks.
        """
        num_landmarks = landmark_info['num']
        for i in range(num_landmarks):
            self.settings['landmarks_active'].append(True)
            self.settings['landmarks_symbols'].append(landmark_info['symbols'][i])
        self.plot_widget.add_landmarks(landmark_info)
        self.plot_settings_dialog.add_landmarks(landmark_info)

    def set_x_range(self, widget):
        if widget == 'button':
            self.plot_widget.plotItem.setLimits(maxXRange=None)
            self.button_range.setEnabled(False)
        elif widget == 'slider':
            x_range = self.slider_range.value()
            self.plot_widget.plotItem.setLimits(maxXRange=x_range)
            self.spinbox_range.setValue(x_range)
            self.button_range.setEnabled(True)
        elif widget == 'spinbox':
            x_range = self.spinbox_range.value()
            self.plot_widget.plotItem.setLimits(maxXRange=x_range)
            self.slider_range.setValue(x_range)
            self.button_range.setEnabled(True)

    def decoder_added(self, receiver_info, landmark_info):
        """
        Do stuff when a new decoder is added.
        """
        self.add_datalines(receiver_info)
        self.add_landmarks(landmark_info)

    def decoder_removed(self):
        """
        Do stuff when a decoderr has been removed.
        """
        self.plot_widget.reset_plot()
        self.plot_settings_dialog.decoder_removed()
        self.button_settings.setEnabled(False)
        self.settings['datalines_active'] = []
        self.settings['datalines_pens'] = []
        self.current_color = 0

    def set_style(self, receiver_index, sensor_index, combobox):
        """
        Sets the line style for a given dataline.
        :param receiver_index: Receiver index of the dataline.
        :param sensor_index: Sensor index of the dataline.
        :param combobox: Combobox containing the style item.
        """
        # Qt.SolidLine, etc.
        qstyle = getattr(Qt, combobox.currentText())
        self.settings['datalines_pens'][receiver_index][sensor_index].setStyle(qstyle)
        self.plot_widget.set_pen(receiver_index, sensor_index)

    def set_color(self, receiver_index, sensor_index):
        # TODO: Refactor color?
        """
        Sets the color for a given dataline.
        :param receiver_index: Receiver index of the dataline.
        :param sensor_index: Sensor_index of the dataline
        :return:
        """
        initial = self.settings['datalines_pens'][receiver_index][sensor_index].color()
        color = QColorDialog.getColor(initial)
        # Is False if the user pressed Cancel
        if color.isValid():
            self.settings['datalines_pens'][receiver_index][sensor_index].setColor(color)
            self.plot_widget.set_pen(receiver_index, sensor_index)
            self.plot_settings_dialog.buttons_color[receiver_index][sensor_index].setStyleSheet("background-color: " + self.settings['datalines_pens'][receiver_index][sensor_index].color().name())

    def set_landmark_symbol(self, landmark_index, combobox):
        """
        Sets a new symbol for a given landmark.
        :param landmark_index: Landmark index.
        :param combobox: Combobox item containing the selected symbol.
        """
        symbol = SYMBOLS[combobox.currentText()]
        #symbol = self.symbols[self.plot_settings_dialog.comboboxes_landmarks_symbol[landmark_index].currentText()]
        self.settings['landmarks_symbols'][landmark_index] = symbol
        self.plot_widget.set_landmark_symbol(landmark_index)

    def show_settings(self):
        """
        Shows the settings menu and puts it into focus.
        """
        self.plot_settings_dialog.show()
        self.plot_settings_dialog.activateWindow()

    def toggle_all_landmarks(self, state):
        """
        Shows/hides all landmarks.
        :param state: 0 -> Hide all; 2 -> Show all
        """
        if state == 0:
            self.plot_settings_dialog.set_all_landmark_checkboxes(False)
            new_state = False
        else:
            state = 2
            self.plot_settings_dialog.checkbox_all_landmarks.setCheckState(Qt.CheckState(state))
            self.plot_settings_dialog.set_all_landmark_checkboxes(True)
            new_state = True

        for landmark_index in range(len(self.settings['landmarks_active'])):
            self.settings['landmarks_active'][landmark_index] = new_state
            # Deactivated
            if not new_state:
                self.plot_widget.clear_landmark(landmark_index)
        self.plot_widget.update_legend()

    def toggle_all_sensor_datalines(self, receiver_index, checkbox):
        """
        Shows/hides all sensor datalines of a given receiver.
        :param receiver_index: Receiver index of the datalines.
        :param checkbox: Checkbox object.
        """
        state = checkbox.checkState()
        if state == 0:
            self.plot_settings_dialog.set_all_sensor_checkboxes(receiver_index, False)
            new_state = False
        else:
            state = 2
            checkbox.setCheckState(Qt.CheckState(state))
            self.plot_settings_dialog.set_all_sensor_checkboxes(receiver_index, True)
            new_state = True

        for sensor_index in range(len(self.settings['datalines_active'][receiver_index])):
            self.settings['datalines_active'][receiver_index][sensor_index] = new_state
            # True -> False
            if not new_state:
                self.plot_widget.clear_dataline(receiver_index, sensor_index)
        self.plot_widget.update_legend()

    def toggle_landmark(self, landmark_index, checkbox):
        """
        Shows/hide a single set of landmarks.
        :param landmark_index: Landmark index of the landmark set.
        """
        state = checkbox.checkState()
        self.settings['landmarks_active'][landmark_index] = state
        # Deactivated
        if not state:
            self.plot_widget.clear_landmark(landmark_index)
        self.data_view.main_view.update_()

        # If necessary, update the "Select all landmarks" checkbox
        all_, any_ = all(self.settings['landmarks_active']), any(self.settings['landmarks_active'])
        state = 2 if all_ else (1 if any_ else 0)
        self.plot_settings_dialog.checkbox_all_landmarks.setCheckState(Qt.CheckState(state))

        self.plot_widget.update_legend()

    def toggle_sensor_dataline(self, receiver_index, sensor_index, checkbox):
        """
        Shows/hides a single dataline.
        :param receiver_index: Receiver index of the dataline.
        :param sensor_index: Sensor index of the dataline.
        :param checkbox: Checkbox object.
        """
        state = checkbox.checkState()
        self.settings['datalines_active'][receiver_index][sensor_index] = state
        # Deactivated
        if not state:
            self.plot_widget.clear_dataline(receiver_index, sensor_index)

        # If necessary, update the receiver checkbox
        all_, any_ = all(self.settings['datalines_active'][receiver_index]), any(self.settings['datalines_active'][receiver_index])
        state = 2 if all_ else (1 if any_ else 0)
        self.plot_settings_dialog.checkboxes_receivers_active[receiver_index].setCheckState(Qt.CheckState(state))

        self.plot_widget.update_legend()

    def toggle_symbol_intervals(self, state):
        """
        Shows/hides symbol intervals (vertical lines).
        :param state: True -> Show; False -> Hide.
        """
        self.settings['symbol_intervals'] = state
        if not state:
            self.plot_widget.clear_symbol_intervals()

    def toggle_symbol_values(self, state):
        """
        Shows/hides symbol values.
        :param state: True -> Show; False -> Hide.
        """
        self.settings['symbol_values'] = state
        if not state:
            self.plot_widget.clear_symbol_values()