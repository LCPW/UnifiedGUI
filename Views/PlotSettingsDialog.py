from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from Views import PlotView
from Utils import ViewUtils


class PlotSettingsDialog(QDialog):
    def __init__(self, plot_view):
        super().__init__()

        self.plot_view = plot_view

        self.setWindowTitle("Plot Settings")
        self.setWindowIcon(ViewUtils.get_icon('stacked_line_chart'))
        self.setModal(False)
        #self.resize(int(round(0.3 * ViewUtils.window_width())), int(round(0.3 * ViewUtils.window_height())))
        self.resize(600, 300)

        self.tabs = QTabWidget()
        self.layout = QVBoxLayout()

        self.checkboxes_decoders_active = []
        self.checkboxes_receivers_active = []
        self.buttons_color_receivers = []
        self.comboboxes_style_receivers = []
        self.checkboxes_additional_datalines_active = []
        self.buttons_additional_datalines_color = []
        self.comboboxes_additional_datalines_style = []
        self.checkboxes_landmarks = []
        self.comboboxes_landmarks_symbol = []
        self.buttons_landmarks_color = []

        self.checkboxes_encoders_active = []
        self.checkboxes_transmitters_active = []
        self.buttons_color_transmitters = []
        self.comboboxes_style_transmitters = []

        self.widget_datalines_decoder = None
        self.widget_datalines_encoder = None

        # General
        self.widget_general = QWidget()
        self.layout_general = QFormLayout()
        self.layout_general.setFieldGrowthPolicy(QFormLayout.FieldsStayAtSizeHint)

        # Show grid
        self.combobox_show_grid = QComboBox()
        self.combobox_show_grid.addItems(['None', 'x-axis only', 'y-axis only', 'x-axis and y-axis'])
        self.combobox_show_grid.activated.connect(self.plot_view.show_grid)
        self.layout_general.addRow(QLabel("Show grid"), self.combobox_show_grid)

        self.widget_general.setLayout(self.layout_general)
        self.tabs.addTab(self.widget_general, "General")

        # Datalines header
        self.widget_datalines = QWidget()
        self.layout_datalines = QFormLayout()
        self.layout_datalines.setFieldGrowthPolicy(QFormLayout.FieldsStayAtSizeHint)

        # Datalines width
        self.spinbox_datalines_width = QSpinBox()
        self.spinbox_datalines_width.setRange(1, 100)
        self.spinbox_datalines_width.valueChanged.connect(self.plot_view.set_datalines_width)
        self.layout_datalines.addRow(QLabel("Datalines width"), self.spinbox_datalines_width)

        self.spinbox_step_size = QSpinBox()
        self.spinbox_step_size.setRange(1, 100)
        self.spinbox_step_size.valueChanged.connect(self.plot_view.set_step_size)
        self.layout_datalines.addRow(QLabel("Step size"), self.spinbox_step_size)

        self.checkboxes_datalines_widget = QWidget()
        self.checkboxes_datalines_layout = QVBoxLayout()
        self.checkboxes_datalines_widget.setLayout(self.checkboxes_datalines_layout)
        self.layout_datalines.addRow(QLabel("Individual"), self.checkboxes_datalines_widget)

        self.widget_datalines.setLayout(self.layout_datalines)
        self.tabs.addTab(self.widget_datalines, "Datalines")

        # Additional datalines
        self.widget_additional_datalines = QWidget()
        self.layout_additional_datalines = QFormLayout()
        self.layout_additional_datalines.setFieldGrowthPolicy(QFormLayout.FieldsStayAtSizeHint)

        # Show additional datalines
        self.checkbox_all_additional_datalines = QCheckBox()
        self.checkbox_all_additional_datalines.setTristate(True)
        self.checkbox_all_additional_datalines.clicked.connect(self.plot_view.toggle_all_additional_datalines)
        self.layout_additional_datalines.addRow(QLabel("Show add. datalines"), self.checkbox_all_additional_datalines)

        # Additional datalines width
        self.spinbox_additional_datalines_width = QSpinBox()
        self.spinbox_additional_datalines_width.setRange(1, 100)
        self.spinbox_additional_datalines_width.valueChanged.connect(self.plot_view.set_additional_datalines_width)
        self.layout_additional_datalines.addRow(QLabel("Add. datalines width"), self.spinbox_additional_datalines_width)

        self.checkboxes_additional_datalines_widget = QWidget()
        self.checkboxes_additional_datalines_layout = QHBoxLayout()
        self.checkboxes_additional_datalines_widget.setLayout(self.checkboxes_additional_datalines_layout)

        self.widget_additional_datalines.setLayout(self.layout_additional_datalines)
        self.tabs.addTab(self.widget_additional_datalines, "Add. datalines")

        # Landmarks header
        self.widget_landmarks = QWidget()
        self.layout_landmarks = QFormLayout()
        self.layout_landmarks.setFieldGrowthPolicy(QFormLayout.FieldsStayAtSizeHint)

        # Show landmarks
        self.checkbox_all_landmarks = QCheckBox()
        self.checkbox_all_landmarks.setTristate(True)
        self.checkbox_all_landmarks.clicked.connect(self.plot_view.toggle_all_landmarks)
        self.layout_landmarks.addRow(QLabel("Show landmarks"), self.checkbox_all_landmarks)

        # Landmarks size
        self.spinbox_landmarks_size = QSpinBox()
        self.spinbox_landmarks_size.setRange(1, 100)
        self.spinbox_landmarks_size.valueChanged.connect(self.plot_view.set_landmarks_size)
        self.layout_landmarks.addRow(QLabel("Landmarks size"), self.spinbox_landmarks_size)

        self.checkboxes_landmarks_widget = QWidget()
        self.checkboxes_landmarks_layout = QHBoxLayout()
        self.checkboxes_landmarks_widget.setLayout(self.checkboxes_landmarks_layout)

        self.widget_landmarks.setLayout(self.layout_landmarks)
        self.tabs.addTab(self.widget_landmarks, "Landmarks")

        # Symbol intervals
        self.widget_symbol_intervals = QWidget()
        self.layout_symbol_intervals = QFormLayout()
        self.layout_symbol_intervals.setFieldGrowthPolicy(QFormLayout.FieldsStayAtSizeHint)

        # Show symbol intervals
        self.checkbox_symbol_intervals = QCheckBox()
        self.checkbox_symbol_intervals.setChecked(True)
        self.checkbox_symbol_intervals.clicked.connect(self.plot_view.toggle_symbol_intervals)

        # Symbol intervals width
        self.spinbox_symbol_intervals_width = QSpinBox()
        self.spinbox_symbol_intervals_width.setRange(1, 100)
        self.spinbox_symbol_intervals_width.valueChanged.connect(self.plot_view.set_symbol_intervals_width)

        # Symbol intervals color
        self.button_symbol_intervals_color = QPushButton()
        self.button_symbol_intervals_color.clicked.connect(self.plot_view.set_symbol_intervals_color)

        self.layout_symbol_intervals.addRow(QLabel("Show symbol intervals"), self.checkbox_symbol_intervals)
        self.layout_symbol_intervals.addRow(QLabel("Symbol intervals width"), self.spinbox_symbol_intervals_width)
        self.layout_symbol_intervals.addRow(QLabel("Symbol intervals color"), self.button_symbol_intervals_color)
        self.widget_symbol_intervals.setLayout(self.layout_symbol_intervals)

        self.tabs.addTab(self.widget_symbol_intervals, "Symbol intervals")

        # Symbol values
        self.widget_symbol_values = QWidget()
        self.layout_symbol_values = QFormLayout()
        self.layout_symbol_values.setFieldGrowthPolicy(QFormLayout.FieldsStayAtSizeHint)

        # Show symbol values
        self.checkbox_symbol_values = QCheckBox()
        self.checkbox_symbol_values.setChecked(True)
        self.checkbox_symbol_values.clicked.connect(self.plot_view.toggle_symbol_values)

        # Symbol values position
        self.combobox_symbol_values_position = QComboBox()
        self.combobox_symbol_values_position.addItems(['Above', 'Below', 'Fixed'])
        self.combobox_symbol_values_position.activated.connect(self.plot_view.set_symbol_values_position)

        # Symbol values fixed height
        self.spinbox_symbol_values_fixed_height = QDoubleSpinBox()
        self.spinbox_symbol_values_fixed_height.setDecimals(2)
        self.spinbox_symbol_values_fixed_height.setRange(-10000, 10000)
        self.spinbox_symbol_values_fixed_height.valueChanged.connect(self.plot_view.set_symbol_values_height)

        # Symbol values size
        self.spinbox_symbol_values_size = QSpinBox()
        self.spinbox_symbol_values_size.setRange(1, 100)
        self.spinbox_symbol_values_size.valueChanged.connect(self.plot_view.set_symbol_values_size)

        self.layout_symbol_values.addRow(QLabel("Show symbol values"), self.checkbox_symbol_values)
        self.layout_symbol_values.addRow(QLabel("Symbol values size"), self.spinbox_symbol_values_size)
        self.layout_symbol_values.addRow(QLabel("Symbol values position"), self.combobox_symbol_values_position)
        self.layout_symbol_values.addRow(QLabel("Symbol values height"), self.spinbox_symbol_values_fixed_height)
        self.widget_symbol_values.setLayout(self.layout_symbol_values)

        self.tabs.addTab(self.widget_symbol_values, "Symbol values")

        button_default_settings = QPushButton("Default settings")
        button_default_settings.clicked.connect(self.plot_view.load_default_settings)

        widget_reset = QWidget()
        widget_reset_layout = QFormLayout()
        widget_reset_layout.setFieldGrowthPolicy(QFormLayout.FieldsStayAtSizeHint)
        widget_reset_layout.addRow(QLabel("Reset"), button_default_settings)
        widget_reset.setLayout(widget_reset_layout)
        self.tabs.addTab(widget_reset, "Reset")

        self.layout.addWidget(self.tabs)
        self.setLayout(self.layout)

    def add_additional_datalines(self, additional_datalines_info):
        def generate_lambda_checkbox(i, o):
            return lambda: self.plot_view.toggle_additional_dataline(i, o)

        def generate_lambda_button(i):
            return lambda: self.plot_view.set_additional_dataline_color(i)

        def generate_lambda_combobox(i, o):
            return lambda: self.plot_view.set_additional_dataline_style(i, o)

        all_, any_ = all(self.plot_view.settings_decoder['additional_datalines_active']), any(self.plot_view.settings_decoder['additional_datalines_active'])
        state = 2 if all_ else (1 if any_ else 0)
        self.checkbox_all_additional_datalines.setCheckState(Qt.CheckState(state))

        num, names = additional_datalines_info['num'], additional_datalines_info['names']
        for dataline_index in range(num):
            w = QWidget()
            w_layout = QVBoxLayout()

            # Checkbox for toggling datalines
            checkbox = QCheckBox(names[dataline_index])
            checkbox.setChecked(self.plot_view.settings_decoder['additional_datalines_active'][dataline_index])
            checkbox.clicked.connect(generate_lambda_checkbox(dataline_index, checkbox))
            self.checkboxes_additional_datalines_active.append(checkbox)

            # Button for selecting color of the datalines
            button_color = QPushButton()
            button_color.setStyleSheet(
                "background-color: " + self.plot_view.settings_decoder['additional_datalines_color'][dataline_index])
            button_color.clicked.connect(generate_lambda_button(dataline_index))
            self.buttons_additional_datalines_color.append(button_color)

            # Combobox for selecting style of the datalines
            combobox = QComboBox()
            combobox.addItems(["SolidLine", "DashLine", "DotLine", "DashDotLine", "DashDotDotLine"])
            combobox.setCurrentText(self.plot_view.settings_decoder['additional_datalines_style'][dataline_index])
            combobox.activated.connect(generate_lambda_combobox(dataline_index, combobox))
            self.comboboxes_additional_datalines_style.append(combobox)

            w_layout.addWidget(checkbox)
            w_layout.addWidget(button_color)
            w_layout.addWidget(combobox)

            w.setLayout(w_layout)
            self.checkboxes_additional_datalines_layout.addWidget(w)
        self.checkboxes_additional_datalines_layout.addStretch(1)
        if num > 0:
            self.layout_additional_datalines.addRow(QLabel("Individual"), self.checkboxes_additional_datalines_widget)

    def add_datalines(self, is_decoder, object_info):
        """
        Add settings for datalines.
        :param is_decoder: Define whether the object is a decoder (True) or encoder (False).
        :param object_info: Information about the decoder/encoder.
        """
        # Helper functions necessary for connecting multiple widgets to the same function
        def generate_lambda_checkbox(is_decoder, i, j, o):
            if is_decoder:
                return lambda: self.plot_view.toggle_sensor_dataline_decoder(i, j, o)
            else:
                return lambda: self.plot_view.toggle_sensor_dataline_encoder(i, j, o)

        def generate_lambda_receiver_checkbox(is_decoder, i, o):
            if is_decoder:
                return lambda: self.plot_view.toggle_all_sensor_datalines_decoder(i, o)
            else:
                return lambda: self.plot_view.toggle_all_sensor_datalines_encoder(i, o)

        def generate_lambda_button(is_decoder, i, j):
            if is_decoder:
                return lambda: self.plot_view.set_color_decoder(i, j)
            else:
                return lambda: self.plot_view.set_color_encoder(i, j)

        def generate_lambda_combobox(is_decoder, i, j, o):
            if is_decoder:
                return lambda: self.plot_view.set_style_decoder(i, j, o)
            else:
                return lambda: self.plot_view.set_style_encoder(i, j, o)

        settings = self.plot_view.settings_decoder
        if is_decoder:
            channel_names_list = object_info['sensor_names']
        else:
            settings = self.plot_view.settings_encoder
            channel_names_list = object_info['channel_names']

        for object_index in range(object_info['num']):
            name = object_info['names'][object_index]
            channel_names = channel_names_list[object_index]

            object_widget = QWidget()
            object_layout = QHBoxLayout()
            checkbox_object = QCheckBox(name)
            checkbox_object.setTristate(True)
            all_, any_ = all(settings['datalines_active'][object_index]), any(settings['datalines_active'][object_index])
            state = 2 if all_ else (1 if any_ else 0)
            checkbox_object.setCheckState(Qt.CheckState(state))
            checkbox_object.clicked.connect(generate_lambda_receiver_checkbox(is_decoder, object_index, checkbox_object))
            object_layout.addWidget(checkbox_object)

            if is_decoder:
                self.checkboxes_decoders_active.append(checkbox_object)
            else:
                self.checkboxes_encoders_active.append(checkbox_object)

            _checkboxes_active = []
            _buttons_color = []
            _comboboxes_style = []
            for channel_index in range(len(channel_names)):
                widget_channel = QWidget()
                layout_channel = QVBoxLayout()

                # Checkbox for toggling datalines
                checkbox = QCheckBox(channel_names[channel_index])
                checkbox.setChecked(settings['datalines_active'][object_index][channel_index])
                checkbox.clicked.connect(generate_lambda_checkbox(is_decoder, object_index, channel_index, checkbox))
                _checkboxes_active.append(checkbox)

                # Button for selecting color of the datalines
                button_color = QPushButton()
                button_color.setStyleSheet("background-color: " + settings['datalines_color'][object_index][channel_index])
                button_color.clicked.connect(generate_lambda_button(is_decoder, object_index, channel_index))
                _buttons_color.append(button_color)

                # Combobox for selecting style of the datalines
                combobox = QComboBox()
                combobox.addItems(["SolidLine", "DashLine", "DotLine", "DashDotLine", "DashDotDotLine"])
                combobox.setCurrentText(settings['datalines_style'][object_index][channel_index])
                combobox.activated.connect(generate_lambda_combobox(is_decoder, object_index, channel_index, combobox))
                _comboboxes_style.append(combobox)

                layout_channel.addWidget(checkbox)
                layout_channel.addWidget(button_color)
                layout_channel.addWidget(combobox)
                widget_channel.setLayout(layout_channel)

                object_layout.addWidget(widget_channel)

            if is_decoder:
                self.checkboxes_receivers_active.append(_checkboxes_active)
                self.buttons_color_receivers.append(_buttons_color)
                self.comboboxes_style_receivers.append(_comboboxes_style)
            else:
                self.checkboxes_transmitters_active.append(_checkboxes_active)
                self.buttons_color_transmitters.append(_buttons_color)
                self.comboboxes_style_transmitters.append(_comboboxes_style)


            object_widget.setLayout(object_layout)
            if is_decoder:
                self.widget_datalines_decoder = object_widget
            else:
                self.widget_datalines_encoder = object_widget
            self.checkboxes_datalines_layout.addWidget(object_widget)

        self.checkboxes_datalines_layout.addStretch(1)

    def add_landmarks(self, landmark_info):
        """
        Add settings for the landmarks.
        :param landmark_info: Information about the landmarks.
        """
        def generate_lambda_landmark_toggle(i, o):
            return lambda: self.plot_view.toggle_landmark(i, o)

        def generate_lambda_landmark_symbol(i, o):
            return lambda: self.plot_view.set_landmark_symbol(i, o)

        def generate_lambda_button(i):
            return lambda: self.plot_view.set_landmark_color(i)

        all_, any_ = all(self.plot_view.settings_decoder['landmarks_active']), any(self.plot_view.settings_decoder['landmarks_active'])
        state = 2 if all_ else (1 if any_ else 0)
        self.checkbox_all_landmarks.setCheckState(Qt.CheckState(state))

        num_landmarks = landmark_info['num']
        for landmark_index in range(num_landmarks):
            widget = QWidget()
            layout = QVBoxLayout()

            # Checkbox to toggle landmark
            checkbox = QCheckBox(landmark_info['names'][landmark_index])
            checkbox.setChecked(self.plot_view.settings_decoder['landmarks_active'][landmark_index])
            checkbox.clicked.connect(generate_lambda_landmark_toggle(landmark_index, checkbox))
            self.checkboxes_landmarks.append(checkbox)

            # Combobox to select symbol
            combobox = QComboBox()
            combobox.addItems(PlotView.SYMBOLS.keys())
            combobox.setCurrentIndex(list(PlotView.SYMBOLS.values()).index(self.plot_view.settings_decoder['landmarks_symbols'][landmark_index]))
            combobox.activated.connect(generate_lambda_landmark_symbol(landmark_index, combobox))
            self.comboboxes_landmarks_symbol.append(combobox)

            # Button for selecting color of the landmark
            button_color = QPushButton()
            button_color.setStyleSheet("background-color: " + self.plot_view.settings_decoder['landmarks_color'][landmark_index])
            button_color.clicked.connect(generate_lambda_button(landmark_index))
            self.buttons_landmarks_color.append(button_color)

            layout.addWidget(checkbox)
            layout.addWidget(combobox)
            layout.addWidget(button_color)

            widget.setLayout(layout)
            self.checkboxes_landmarks_layout.addWidget(widget)
        self.checkboxes_landmarks_layout.addStretch(1)
        if num_landmarks > 0:
            self.layout_landmarks.addRow(QLabel("Individual"), self.checkboxes_landmarks_widget)

    def decoder_added(self):
        """
        Edit settings dialog entries accordingly when a decoder is added.
        """
        # General
        self.combobox_show_grid.setCurrentText(self.plot_view.settings_general['show_grid'])
        # Datalines
        self.spinbox_step_size.setValue(self.plot_view.settings_general['step_size'])
        self.spinbox_datalines_width.setValue(self.plot_view.settings_general['datalines_width'])

        # Additional datalines
        self.spinbox_additional_datalines_width.setValue(self.plot_view.settings_decoder['additional_datalines_width'])

        # Landmarks
        self.spinbox_landmarks_size.setValue(self.plot_view.settings_decoder['landmarks_size'])

        # Symbol intervals
        self.checkbox_symbol_intervals.setChecked(self.plot_view.settings_decoder['symbol_intervals'])
        self.spinbox_symbol_intervals_width.setValue(self.plot_view.settings_decoder['symbol_intervals_width'])
        self.button_symbol_intervals_color.setStyleSheet("background-color: " + self.plot_view.settings_decoder['symbol_intervals_color'])

        # Symbol values
        self.checkbox_symbol_values.setChecked(self.plot_view.settings_decoder['symbol_values'])
        self.combobox_symbol_values_position.setCurrentText(self.plot_view.settings_decoder['symbol_values_position'])
        self.spinbox_symbol_values_size.setValue(self.plot_view.settings_decoder['symbol_values_size'])
        self.spinbox_symbol_values_fixed_height.setValue(self.plot_view.settings_decoder['symbol_values_fixed_height'])
        if self.plot_view.settings_decoder['symbol_values_position'] == "Fixed":
            self.spinbox_symbol_values_fixed_height.setEnabled(True)
        else:
            self.spinbox_symbol_values_fixed_height.setEnabled(False)

    def decoder_removed(self):
        """
        Reset everything after decoder has been removed.
        """
        self.checkboxes_decoders_active = []
        self.checkboxes_receivers_active = []
        self.buttons_color_receivers = []
        self.comboboxes_style_receivers = []

        # # https://stackoverflow.com/questions/4528347/clear-all-widgets-in-a-layout-in-pyqt
        # for i in reversed(range(self.checkboxes_datalines_layout.count())):
        #     self.checkboxes_datalines_layout.removeWidget(self.checkboxes_datalines_layout.itemAt(i).widget())
        self.checkboxes_datalines_layout.removeWidget(self.widget_datalines_decoder)
        self.widget_datalines_decoder = None

        self.checkboxes_landmarks = []
        self.comboboxes_landmarks_symbol = []

        for i in reversed(range(self.checkboxes_landmarks_layout.count())):
            self.checkboxes_landmarks_layout.removeWidget(self.checkboxes_landmarks_layout.itemAt(i).widget())

        self.hide()

    def encoder_added(self):
        """
        Edit settings dialog entries accordingly when a decoder is added.
        """
        # General
        self.combobox_show_grid.setCurrentText(self.plot_view.settings_general['show_grid'])
        # Datalines
        self.spinbox_step_size.setValue(self.plot_view.settings_general['step_size'])
        self.spinbox_datalines_width.setValue(self.plot_view.settings_general['datalines_width'])

    def encoder_removed(self):
        """
        Reset everything after encoder has been removed.
        """
        self.checkboxes_encoders_active = []
        self.checkboxes_transmitters_active = []
        self.buttons_color_transmitters = []
        self.comboboxes_style_transmitters = []

        self.checkboxes_datalines_layout.removeWidget(self.widget_datalines_encoder)
        self.widget_datalines_encoder = None

    def set_all_additional_datalines_checkboxes(self, state):
        """
        Sets alls additional datalines checkboxes to a given state.
        :param state: New state of the additional datalines checkboxes.
        """
        for dataline_index in range(len(self.checkboxes_additional_datalines_active)):
            self.checkboxes_additional_datalines_active[dataline_index].setChecked(state)

    def set_all_landmark_checkboxes(self, state):
        """
        Sets all landmark checkboxes to the given state.
        :param state: New state of the landmark checkboxes.
        """
        for landmark_index in range(len(self.checkboxes_landmarks)):
            self.checkboxes_landmarks[landmark_index].setChecked(state)

    def set_all_sensor_checkboxes(self, receiver_index, state):
        """
        Sets all sensor datalines checkboxes for a given receiver to the given state.
        :param receiver_index: Index of the receiver.
        :param state: New state of the checkboxes.
        """
        for sensor_index in range(len(self.checkboxes_receivers_active[receiver_index])):
            self.checkboxes_receivers_active[receiver_index][sensor_index].setChecked(state)

    def set_all_channel_checkboxes(self, encoder_index, state):
        """
        Sets all sensor datalines checkboxes for a given encoder to the given state.
        :param encoder_index: Index of the encoder.
        :param state: New state of the checkboxes.
        """
        for channel_index in range(len(self.checkboxes_transmitters_active[encoder_index])):
            self.checkboxes_transmitters_active[encoder_index][channel_index].setChecked(state)