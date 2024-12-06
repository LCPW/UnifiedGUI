from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
import numpy as np

from Views import PlotWidgetView, PlotSettingsDialog
from Utils.PlotSettings import PlotSettings
from Utils.Settings import SettingsStore
from Utils import ViewUtils


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
}


class PlotView(QWidget):
    """
    This widget contains the plot widget as well as the toolbar above the plot, including a button for the plot settings.
    """
    def __init__(self, data_view):
        super().__init__()

        self.settings_object = None

        layout = QVBoxLayout()

        self.data_view = data_view
        self.plot_settings_dialog = PlotSettingsDialog.PlotSettingsDialog(self)
        self.plot_widget = PlotWidgetView.PlotWidgetView(self)

        self.toolbar = QToolBar()

        # X range settings
        self.label_range = QLabel("X-Axis Range[s]")
        self.button_range = QToolButton()
        self.button_range.setToolTip("Auto (no limit)")
        self.button_range.setIcon(ViewUtils.get_icon('all_inclusive'))
        self.button_range.setEnabled(False)
        self.button_range.clicked.connect(lambda: self.set_x_range('button'))
        self.slider_range = QSlider(Qt.Horizontal)
        self.slider_range.setEnabled(False)
        self.slider_range.sizeHint = QSize(int(round(0.3*ViewUtils.window_width())), int(round(self.slider_range.height())))
        self.slider_range.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Maximum)
        self.slider_range.setRange(1, 100)
        self.slider_range.setValue(10)
        self.slider_range.sliderMoved.connect(lambda: self.set_x_range('slider'))
        self.spinbox_range = QDoubleSpinBox()
        self.spinbox_range.setEnabled(False)
        self.spinbox_range.setDecimals(1)
        self.spinbox_range.setRange(0.1, 100)
        self.spinbox_range.setValue(10)
        self.spinbox_range.setSingleStep(1.0)
        self.spinbox_range.valueChanged.connect(lambda: self.set_x_range('spinbox'))

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
        self.button_settings.setToolTip("Plot settings")
        self.button_settings.setIcon(ViewUtils.get_icon('stacked_line_chart'))
        self.button_settings.setEnabled(False)
        self.button_settings.clicked.connect(self.show_settings)
        self.toolbar.addWidget(self.button_settings)

        # Scrollbar
        self.scrollbar = QScrollBar(Qt.Horizontal)
        self.scrollbar.sliderMoved.connect(self.scrollbar_moved)

        layout.addWidget(self.toolbar)
        layout.addWidget(self.plot_widget)
        layout.addWidget(self.scrollbar)
        self.setLayout(layout)

    @property
    def settings_decoder(self):
        return self.settings_object.settings_decoder

    @property
    def settings_encoder(self):
        return self.settings_object.settings_encoder

    @property
    def settings_general(self):
        return self.settings_object.settings_general

    def add_additional_datalines(self, additional_datalines_info):
        """
        Adds new additional datalines.
        This function is usually executed when a new decoder has been added.
        :param additional_datalines_info: Information about the new datalines.
        """
        self.plot_widget.add_additional_datalines(additional_datalines_info)
        self.plot_settings_dialog.add_additional_datalines(additional_datalines_info)

    def add_datalines_receiver(self, receiver_info):
        """
        Adds new datalines.
        This function is usually executed when a new decoder has been added.
        :param receiver_info: Information about the receivers.
        """
        self.plot_widget.add_datalines_receiver(receiver_info)
        self.plot_settings_dialog.add_datalines(True, receiver_info)

    def add_datalines_encoder(self, transmitter_info):
        """
        Adds new datalines.
        This function is usually executed when a new encoder has been added.
        :param transmitter_info: Information about the transmitters.
        """
        self.plot_widget.add_datalines_transmitter(transmitter_info)
        self.plot_settings_dialog.add_datalines(False, transmitter_info)

    def add_landmarks(self, landmark_info):
        """
        Adds new landmarks.
        This function is usually executed when a new decoder has been added.
        :param landmark_info: Information about the landmarks.
        """
        self.plot_widget.add_landmarks(landmark_info)
        self.plot_settings_dialog.add_landmarks(landmark_info)

    def decoder_added(self, decoder_info):
        """
        Do stuff when a new decoder is added.
        Loads settings and creates datalines/landmarks.
        :param decoder_info: Information about decoder.
        """
        if self.settings_object is None:
            self.settings_object = PlotSettings.PlotSettings()
            self.settings_object.load_file_default_settings_decoder(decoder_info)
            self.init_plot()
        else:
            self.settings_object.load_file_default_settings_decoder(decoder_info)

        self.add_datalines_receiver(decoder_info['receivers'])
        self.add_additional_datalines(decoder_info['additional_datalines'])
        self.add_landmarks(decoder_info['landmarks'])
        self.plot_settings_dialog.decoder_added()

    def decoder_clear(self):
        """
        Clears elements from the plot.
        """
        self.plot_widget.clear_()

    def decoder_removed(self):
        """
        Do stuff when the decoder has been removed.
        Saves settings and resets plot.
        """
        self.settings_object.save_decoder()
        if self.settings_object.is_empty():
            self.destroy_plot()
            self.plot_settings_dialog.decoder_removed()

    def destroy_plot(self):
        self.settings_object.save_general()
        self.plot_widget.reset_plot()
        self.button_settings.setEnabled(False)
        self.settings_object = None

    def encoder_added(self, encoder_info):
        """
        Do stuff when a new encoder is added.
        Loads settings and creates datalines/landmarks.
        :param encoder_info: Information about the encoder.
        """
        if self.settings_object is None:
            self.settings_object = PlotSettings.PlotSettings()
            self.settings_object.load_file_default_settings_encoder(encoder_info)
            self.init_plot()
        else:
            self.settings_object.load_file_default_settings_encoder(encoder_info)

        self.add_datalines_encoder(encoder_info['transmitters'])
        self.plot_settings_dialog.encoder_added()

    def encoder_clear(self):
        """
        Clears elements from the plot.
        """
        self.plot_widget.clear_()

    def encoder_removed(self):
        """
        Do stuff when the encoder has been removed.
        Saves settings and resets plot.
        """
        self.settings_object.save_encoder()
        if self.settings_object.is_empty():
            self.destroy_plot()
            self.plot_settings_dialog.encoder_removed()

    def init_plot(self):
        self.settings_object.load_file_default_settings_general()
        self.init_x_range()
        self.show_grid(self.settings_general['show_grid'])
        self.button_settings.setEnabled(True)

    def init_x_range(self):
        """
        Initializes the settings for the x-range above the plot accordingly.
        """
        self.slider_range.setRange(max(self.settings_general['x_range_min'], 1), self.settings_general['x_range_max'])
        self.slider_range.setValue(int(round(self.settings_general['x_range_value'])))
        self.spinbox_range.setDecimals(self.settings_general['x_range_decimals'])
        self.spinbox_range.setRange(self.settings_general['x_range_min'], self.settings_general['x_range_max'])
        self.spinbox_range.setValue(self.settings_general['x_range_value'])
        # Actually set the x range
        self.plot_widget.plotItem.setLimits(maxXRange=self.settings_general['x_range_value'])
        self.slider_range.setEnabled(True)
        self.spinbox_range.setEnabled(True)
        if self.settings_general['x_range_active']:
            self.button_range.setEnabled(True)

    def load_default_settings(self):
        """
        Loads default settings which they user might have provided in the decoder implementation.
        This is executed if the user clicked on the 'Default settings' button in the plot settings dialog.
        """
        decoder_info = self.data_view.view.controller.get_decoder_info()
        self.settings_object.load_default_settings(decoder_info)
        self.plot_settings_dialog.hide()
        self.plot_settings_dialog = PlotSettingsDialog.PlotSettingsDialog(self)
        self.plot_settings_dialog.add_datalines_receiver(decoder_info['receivers'])
        self.plot_settings_dialog.add_landmarks(decoder_info['landmarks'])
        self.plot_settings_dialog.decoder_added()
        self.plot_settings_dialog.show()
        self.plot_widget.settings_updated()

    def set_additional_dataline_color(self, dataline_index):
        """
        Sets the color for a given additional dataline.
        :param dataline_index: Index of the additional dataline.
        """
        initial_color = QColor(self.settings_decoder['additional_datalines_color'][dataline_index])
        color = QColorDialog.getColor(initial_color)
        # Is False if the user pressed Cancel
        if color.isValid():
            self.settings_decoder['additional_datalines_color'][dataline_index] = color.name()
            self.plot_widget.set_additional_dataline_pen(dataline_index)
            self.plot_settings_dialog.buttons_additional_datalines_color[dataline_index].setStyleSheet("background-color: " + color.name())

    def set_additional_dataline_style(self, dataline_index, combobox):
        """
        Sets the line style for a given dataline (Qt.SolidLine, etc.).
        :param dataline_index: Index of the additional dataline.
        :param combobox: Combobox containing the style item.
        """
        self.settings_decoder['additional_datalines_style'][dataline_index] = combobox.currentText()
        self.plot_widget.set_additional_dataline_pen(dataline_index)

    def set_additional_datalines_width(self, width):
        """
        Sets the width for all additional datalines.
        :param width: New width of the additional datalines.
        """
        self.settings_decoder['additional_datalines_width'] = width
        self.plot_widget.set_additional_dataline_pens()

    def set_color_decoder(self, decoder_index, sensor_index):
        """
        Sets the color for a given dataline.
        :param decoder_index: Decoder index of the dataline.
        :param sensor_index: Sensor_index of the dataline
        """
        initial_color = QColor(self.settings_decoder['datalines_color'][decoder_index][sensor_index])
        color = QColorDialog.getColor(initial_color)
        # Is False if the user pressed Cancel
        if color.isValid():
            self.settings_decoder['datalines_color'][decoder_index][sensor_index] = color.name()
            self.plot_widget.set_dataline_pen(True, decoder_index, sensor_index)
            self.plot_settings_dialog.buttons_color_receivers[decoder_index][sensor_index].setStyleSheet("background-color: " + color.name())

    def set_color_encoder(self, encoder_index, channel_index):
        """
        Sets the color for a given dataline.
        :param encoder_index: Encoder index of the dataline.
        :param channel_index: Channel index of the dataline
        """
        initial_color = QColor(self.settings_encoder['datalines_color'][encoder_index][channel_index])
        color = QColorDialog.getColor(initial_color)
        # Is False if the user pressed Cancel
        if color.isValid():
            self.settings_encoder['datalines_color'][encoder_index][channel_index] = color.name()
            self.plot_widget.set_dataline_pen(False, encoder_index, channel_index)
            self.plot_settings_dialog.buttons_color_transmitters[encoder_index][channel_index].setStyleSheet("background-color: " + color.name())

    def set_datalines_width(self, width):
        """
        Sets the width for all datalines.
        :param width: New width of the datalines.
        """
        self.settings_general['datalines_width'] = width
        self.plot_widget.set_dataline_pens(True)
        self.plot_widget.set_dataline_pens(False)

    def set_landmark_color(self, landmark_index):
        """
        Sets the color of the symbols of a given landmark set.
        :param landmark_index: Index of the landmark.
        """
        initial_color = QColor(self.settings_decoder['landmarks_color'][landmark_index])
        color = QColorDialog.getColor(initial_color)
        # Is False if the user pressed Cancel
        if color.isValid():
            self.settings_decoder['landmarks_color'][landmark_index] = color.name()
            self.plot_widget.set_landmark_pen(landmark_index)
            self.plot_settings_dialog.buttons_landmarks_color[landmark_index].setStyleSheet("background-color: " + color.name())

    def set_landmarks_size(self, size):
        """
        Sets the size for the landmarks.
        :param size: New size.
        """
        self.settings_decoder['landmarks_size'] = size
        self.plot_widget.set_landmark_pens()

    def set_landmark_symbol(self, landmark_index, combobox):
        """
        Sets a new symbol for a given landmark.
        :param landmark_index: Landmark index.
        :param combobox: Combobox item containing the selected symbol.
        """
        symbol = SYMBOLS[combobox.currentText()]
        self.settings_decoder['landmarks_symbols'][landmark_index] = symbol
        self.plot_widget.set_landmark_pen(landmark_index)

    def set_step_size(self, step_size):
        """
        Sets the step size for values to be shown in the live plot.
        :param step_size: New step size.
        """
        self.settings_general['step_size'] = step_size

    def set_style_decoder(self, decoder_index, sensor_index, combobox):
        """
        Sets the line style for a given dataline (Qt.SolidLine, etc.).
        :param decoder_index: Decoder index of the dataline.
        :param sensor_index: Sensor index of the dataline.
        :param combobox: Combobox containing the style item.
        """
        self.settings_decoder['datalines_style'][decoder_index][sensor_index] = combobox.currentText()
        self.plot_widget.set_dataline_pen(True, decoder_index, sensor_index)

    def set_style_encoder(self, encoder_index, channel_index, combobox):
        """
        Sets the line style for a given dataline (Qt.SolidLine, etc.).
        :param encoder_index: Encoder index of the dataline.
        :param channel_index: Channel index of the dataline.
        :param combobox: Combobox containing the style item.
        """
        self.settings_encoder['datalines_style'][encoder_index][channel_index] = combobox.currentText()
        self.plot_widget.set_dataline_pen(False, encoder_index, channel_index)

    def set_symbol_intervals_color(self):
        """
        Sets the color of the vertical lines that indicate symbol intervals.
        """
        initial_color = QColor(self.settings_decoder['symbol_intervals_color'])
        color = QColorDialog.getColor(initial_color)
        # Is False if the user pressed Cancel
        if color.isValid():
            self.settings_decoder['symbol_intervals_color'] = color.name()
            self.plot_widget.set_symbol_intervals_pen()
            self.plot_settings_dialog.button_symbol_intervals_color.setStyleSheet("background-color: " + color.name())
        self.plot_widget.set_symbol_intervals_pen()

    def set_symbol_intervals_width(self, width):
        """
        Sets the width of the vertical lines that indicate symbol intervals.
        :param width: Width of the vertical lines.
        """
        self.settings_decoder['symbol_intervals_width'] = width
        self.plot_widget.set_symbol_intervals_pen()

    def set_symbol_values_height(self, height):
        """
        Sets the height for the symbol values if fixed height is used.
        :param height: Fixed height of the symbol values.
        """
        self.settings_decoder['symbol_values_fixed_height'] = height
        self.plot_widget.clear_symbol_values()

    def set_symbol_values_position(self, index):
        """
        Sets the position of the symbol values.
        :param index: Index of the position (Above = 0, Below = 1, Fixed = 2)
        """
        if index == 0:
            position = "Above"
            self.plot_settings_dialog.spinbox_symbol_values_fixed_height.setEnabled(False)
        elif index == 1:
            position = "Below"
            self.plot_settings_dialog.spinbox_symbol_values_fixed_height.setEnabled(False)
        else:
            position = "Fixed"
            self.plot_settings_dialog.spinbox_symbol_values_fixed_height.setEnabled(True)
        self.settings_decoder['symbol_values_position'] = position
        self.plot_widget.clear_symbol_values()

    def set_symbol_values_size(self, size):
        """
        Sets font size for symbol values
        :param size: font size.
        """
        self.settings_decoder['symbol_values_size'] = size
        self.plot_widget.set_symbol_values_size()

    def set_x_range(self, widget):
        """
        Sets the X range of the live plot in seconds.
        X range defines which time interval is shown in the plot when set to autoscroll.
        Example: X range = 5 means that only the last 5 seconds are shown before the plot moves to the right.
        :param widget: The widget responsible for the X range change.
        """
        auto_scroll_enabled = self.plot_widget.autoscroll
        if widget == 'button':
            self.plot_widget.plotItem.setLimits(maxXRange=None, xMin=None)
            self.settings_general['x_range_active'] = False
            self.button_range.setEnabled(False)
        elif widget == 'slider':
            x_range = self.slider_range.value()
            self.plot_widget.plotItem.setLimits(maxXRange=x_range)
            self.settings_general['x_range_value'] = x_range
            self.settings_general['x_range_active'] = True
            self.spinbox_range.setValue(x_range)
            self.button_range.setEnabled(True)
        elif widget == 'spinbox':
            x_range = self.spinbox_range.value()
            self.plot_widget.plotItem.setLimits(maxXRange=x_range)
            self.settings_general['x_range_value'] = x_range
            self.settings_general['x_range_active'] = True
            self.slider_range.setValue(int(round(x_range)))
            self.button_range.setEnabled(True)
        self.update_x_range(auto_scroll_enabled)

    def show_grid(self, index):
        """
        Enables/disables live plot grid for x-axis and/or y-axis.
        :param index: Combobox index = {0, 1, 2, 3}
        """
        if index == 0:
            show_grid = 'None'
        elif index == 1:
            show_grid = 'x-axis only'
        elif index == 2:
            show_grid = 'y-axis only'
        else:
            show_grid = 'x-axis and y-axis'
        self.settings_general['show_grid'] = show_grid
        self.plot_widget.showGrid(
            x=self.settings_general['show_grid'] in ['x-axis only', 'x-axis and y-axis'],
            y=self.settings_general['show_grid'] in ['y-axis only', 'x-axis and y-axis'])

    def show_settings(self):
        """
        Shows the settings menu and puts it into focus.
        """
        self.plot_settings_dialog.show()
        self.plot_settings_dialog.activateWindow()

    def toggle_all_additional_datalines(self, state):
        """
        Shows/hides all additional datalines.
        :param state: 0 -> Hide all; 2 -> Show all
        """
        if state == 0:
            self.plot_settings_dialog.set_all_additional_datalines_checkboxes(False)
            new_state = False
        else:
            state = 2
            self.plot_settings_dialog.checkbox_all_additional_datalines.setCheckState(Qt.CheckState(state))
            self.plot_settings_dialog.set_all_additional_datalines_checkboxes(True)
            new_state = True

        for dataline_index in range(len(self.settings_decoder['additional_datalines_active'])):
            self.settings_decoder['additional_datalines_active'][dataline_index] = new_state
            # True -> False
            if not new_state:
                self.plot_widget.clear_additional_dataline(dataline_index)
        self.plot_widget.update_legend()

    def toggle_additional_dataline(self, dataline_index, checkbox):
        """
        Shows/hides a single additional dataline.
        :param dataline_index: Index of the additional datalines.
        :param checkbox: Checkbox object.
        """
        state = checkbox.checkState()
        self.settings_decoder['additional_datalines_active'][dataline_index] = state
        # Deactivated
        if not state:
            self.plot_widget.clear_additional_dataline(dataline_index)

        # If necessary, update the checkbox
        all_, any_ = all(self.settings_decoder['additional_datalines_active']), any(self.settings_decoder['additional_datalines_active'])
        state = 2 if all_ else (1 if any_ else 0)
        self.plot_settings_dialog.checkbox_all_additional_datalines.setCheckState(Qt.CheckState(state))

        self.plot_widget.update_legend()

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

        for landmark_index in range(len(self.settings_decoder['landmarks_active'])):
            self.settings_decoder['landmarks_active'][landmark_index] = new_state
            # Deactivated
            if not new_state:
                self.plot_widget.clear_landmark(landmark_index)
        self.plot_widget.update_legend()

    def toggle_all_sensor_datalines_decoder(self, receiver_index, checkbox):
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

        for sensor_index in range(len(self.settings_decoder['datalines_active'][receiver_index])):
            self.settings_decoder['datalines_active'][receiver_index][sensor_index] = new_state
            # True -> False
            if not new_state:
                self.plot_widget.clear_dataline_receiver(receiver_index, sensor_index)
        self.plot_widget.update_legend()

    def toggle_all_sensor_datalines_encoder(self, encoder_index, checkbox):
        """
        Shows/hides all sensor datalines of a given encoder.
        :param encoder_index: Encoder index of the datalines.
        :param checkbox: Checkbox object.
        """
        state = checkbox.checkState()
        if state == 0:
            self.plot_settings_dialog.set_all_channel_checkboxes(encoder_index, False)
            new_state = False
        else:
            state = 2
            checkbox.setCheckState(Qt.CheckState(state))
            self.plot_settings_dialog.set_all_channel_checkboxes(encoder_index, True)
            new_state = True

        for channel_index in range(len(self.settings_encoder['datalines_active'][encoder_index])):
            self.settings_encoder['datalines_active'][encoder_index][channel_index] = new_state
            # True -> False
            if not new_state:
                self.plot_widget.clear_dataline_transmitter(encoder_index, channel_index)
        self.plot_widget.update_legend()

    def toggle_landmark(self, landmark_index, checkbox):
        """
        Shows/hide a single set of landmarks.
        :param landmark_index: Landmark index of the landmark set.
        """
        state = checkbox.checkState()
        self.settings_decoder['landmarks_active'][landmark_index] = state
        # Deactivated
        if not state:
            self.plot_widget.clear_landmark(landmark_index)
        self.data_view.view.update_()

        # If necessary, update the "Select all landmarks" checkbox
        all_, any_ = all(self.settings_decoder['landmarks_active']), any(self.settings_decoder['landmarks_active'])
        state = 2 if all_ else (1 if any_ else 0)
        self.plot_settings_dialog.checkbox_all_landmarks.setCheckState(Qt.CheckState(state))

        self.plot_widget.update_legend()

    def toggle_sensor_dataline_decoder(self, receiver_index, sensor_index, checkbox):
        """
        Shows/hides a single dataline.
        :param receiver_index: Receiver index of the dataline.
        :param sensor_index: Sensor index of the dataline.
        :param checkbox: Checkbox object.
        """
        state = checkbox.checkState()
        self.settings_decoder['datalines_active'][receiver_index][sensor_index] = state

        # Deactivated
        if not state:
            self.plot_widget.clear_dataline_receiver(receiver_index, sensor_index)

        # If necessary, update the receiver checkbox
        all_, any_ = all(self.settings_decoder['datalines_active'][receiver_index]), any(self.settings_decoder['datalines_active'][receiver_index])
        state = 2 if all_ else (1 if any_ else 0)
        self.plot_settings_dialog.checkboxes_decoders_active[receiver_index].setCheckState(Qt.CheckState(state))

        self.plot_widget.update_legend()

    def toggle_sensor_dataline_encoder(self, encoder_index, channel_index, checkbox):
        """
        Shows/hides a single dataline.
        :param encoder_index: Transmitter index of the dataline.
        :param channel_index: Channel index of the dataline.
        :param checkbox: Checkbox object.
        """
        state = checkbox.checkState()
        self.settings_encoder['datalines_active'][encoder_index][channel_index] = state

        # Deactivated
        if not state:
            self.plot_widget.clear_dataline_transmitter(encoder_index, channel_index)

        # If necessary, update the receiver checkbox
        all_, any_ = all(self.settings_encoder['datalines_active'][encoder_index]), any(self.settings_encoder['datalines_active'][encoder_index])
        state = 2 if all_ else (1 if any_ else 0)
        self.plot_settings_dialog.checkboxes_encoders_active[encoder_index].setCheckState(Qt.CheckState(state))

        self.plot_widget.update_legend()

    def toggle_symbol_intervals(self, state):
        """
        Shows/hides symbol intervals (vertical lines).
        :param state: True -> Show; False -> Hide.
        """
        self.settings_decoder['symbol_intervals'] = state
        if not state:
            self.plot_widget.clear_symbol_intervals()

    def toggle_symbol_values(self, state):
        """
        Shows/hides symbol values.
        :param state: True -> Show; False -> Hide.
        """
        self.settings_decoder['symbol_values'] = state
        if not state:
            self.plot_widget.clear_symbol_values()

    def update_(self, decoded, encoded):
        """
        Updates this widget with new information from the decoder.
        :param decoded: Decoder value updates.
        :param encoded: Encoder value updates.
        """
        self.update_scroll_bar(decoded, encoded)
        self.plot_widget.update_(decoded, encoded)

    def update_scroll_bar(self, decoded, encoded):
        """
        Updates the length of the scrollbar accordingly.
        The value of the scrollbar always indicates the left value of the current range.
        :param decoded: Decoder value updates.
        :param encoded: Encoder value updates.
        """
        min_timestamp, max_timestamp = 0, 0
        if decoded is not None:
            min_timestamp, max_timestamp = decoded['min_timestamp'], decoded['max_timestamp']

            if encoded is not None:
                min_timestamp = min(min_timestamp, encoded['min_timestamp'])
                max_timestamp = max(max_timestamp, encoded['max_timestamp'])
        else:
            min_timestamp, max_timestamp = encoded['min_timestamp'], encoded['max_timestamp']

        x_range_active, x_value = self.settings_general['x_range_active'], self.settings_general['x_range_value']
        if x_range_active:
            interval = max_timestamp - min_timestamp - x_value
            # Clip negative values
            interval = interval if interval > 0 else 0
            self.scrollbar.setRange(0, int(interval * SettingsStore.settings['SCROLLBAR_GRANULARITY']))
        else:
            self.scrollbar.setRange(0, 0)

    def update_x_range(self, enable_autoscroll=False):
        """
        Updates the X range of the plot.
        This function is called whenever the user modifies the X range.
        :param enable_autoscroll: Whether autoscroll should resume after the x-range has been updated.
        """
        scrollbar_value = self.scrollbar.value()
        self.plot_widget.update_x_range(scrollbar_value, enable_autoscroll)

    def scrollbar_moved(self):
        """
        This function is called whenever the user moves the scrollbar.
        """
        self.update_x_range(enable_autoscroll=False)