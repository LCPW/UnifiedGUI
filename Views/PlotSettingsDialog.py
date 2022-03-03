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
        self.setWindowIcon(ViewUtils.get_icon('settings'))
        self.setModal(False)

        self.layout = QVBoxLayout()

        self.checkboxes_receivers_active = []
        self.checkboxes_active = []
        self.buttons_color = []
        self.comboboxes_style = []
        self.checkboxes_landmarks = []
        self.comboboxes_landmarks_symbol = []
        self.buttons_landmarks_color = []

        # Datalines header
        self.label_datalines = QLabel("Datalines")
        self.label_datalines.setObjectName("menu_header")
        self.widget_datalines = QWidget()
        self.layout_datalines = QFormLayout()

        # Datalines width
        self.label_datalines_width = QLabel("Datalines width")
        self.spinbox_datalines_width = QSpinBox()
        self.spinbox_datalines_width.setRange(1, 100)
        self.spinbox_datalines_width.valueChanged.connect(self.plot_view.set_datalines_width)
        self.layout_datalines.addRow(self.label_datalines_width, self.spinbox_datalines_width)

        self.widget_datalines.setLayout(self.layout_datalines)

        self.checkboxes_datalines_widget = QWidget()
        self.checkboxes_datalines_layout = QVBoxLayout()
        self.checkboxes_datalines_widget.setLayout(self.checkboxes_datalines_layout)

        # Landmarks header
        self.label_landmarks = QLabel("Landmarks")
        self.label_landmarks.setObjectName("menu_header")

        self.widget_landmarks = QWidget()
        self.layout_landmarks = QFormLayout()

        # Show landmarks
        self.label_show_all_landmarks = QLabel("Show landmarks")
        self.checkbox_all_landmarks = QCheckBox()
        self.checkbox_all_landmarks.setTristate(True)
        self.checkbox_all_landmarks.clicked.connect(self.plot_view.toggle_all_landmarks)
        self.layout_landmarks.addRow(self.label_show_all_landmarks, self.checkbox_all_landmarks)

        # Landmarks size
        self.label_landmarks_size = QLabel("Landmarks size")
        self.spinbox_landmarks_size = QSpinBox()
        self.spinbox_landmarks_size.setRange(1, 100)
        self.spinbox_landmarks_size.valueChanged.connect(self.plot_view.set_landmarks_size)
        self.layout_landmarks.addRow(self.label_landmarks_size, self.spinbox_landmarks_size)

        self.widget_landmarks.setLayout(self.layout_landmarks)

        self.checkboxes_landmarks_widget = QWidget()
        self.checkboxes_landmarks_layout = QHBoxLayout()
        self.checkboxes_landmarks_widget.setLayout(self.checkboxes_landmarks_layout)

        # Symbol intervals
        self.label_symbol_intervals = QLabel("Symbol intervals")
        self.label_symbol_intervals.setObjectName("menu_header")
        self.widget_symbol_intervals = QWidget()
        self.layout_symbol_intervals = QFormLayout()

        # Show symbol intervals
        self.label_show_symbol_intervals = QLabel("Show symbol intervals")
        self.checkbox_symbol_intervals = QCheckBox()
        self.checkbox_symbol_intervals.setChecked(True)
        self.checkbox_symbol_intervals.clicked.connect(self.plot_view.toggle_symbol_intervals)

        # Symbol intervals width
        self.label_symbol_intervals_width = QLabel("Symbol intervals width")
        self.spinbox_symbol_intervals_width = QSpinBox()
        self.spinbox_symbol_intervals_width.setRange(1, 100)
        self.spinbox_symbol_intervals_width.valueChanged.connect(self.plot_view.set_symbol_intervals_width)

        # Symbol intervals color
        self.label_symbol_intervals_color = QLabel("Symbol intervals color")
        self.button_symbol_intervals_color = QPushButton()
        self.button_symbol_intervals_color.clicked.connect(self.plot_view.set_symbol_intervals_color)

        self.layout_symbol_intervals.addRow(self.label_show_symbol_intervals, self.checkbox_symbol_intervals)
        self.layout_symbol_intervals.addRow(self.label_symbol_intervals_width, self.spinbox_symbol_intervals_width)
        self.layout_symbol_intervals.addRow(self.label_symbol_intervals_color, self.button_symbol_intervals_color)
        self.widget_symbol_intervals.setLayout(self.layout_symbol_intervals)

        # Symbol values
        self.label_symbol_values = QLabel("Symbol values")
        self.label_symbol_values.setObjectName("menu_header")
        self.widget_symbol_values = QWidget()
        self.layout_symbol_values = QFormLayout()

        # Show symbol values
        self.label_show_symbol_values = QLabel("Show symbol values")
        self.checkbox_symbol_values = QCheckBox()
        self.checkbox_symbol_values.setChecked(True)
        self.checkbox_symbol_values.clicked.connect(self.plot_view.toggle_symbol_values)

        # Symbol values position
        self.label_symbol_values_position = QLabel("Symbol values position")
        self.combobox_symbol_values_position = QComboBox()
        self.combobox_symbol_values_position.addItems(['Above', 'Below', 'Fixed'])
        self.combobox_symbol_values_position.activated.connect(self.plot_view.set_symbol_values_position)

        # Symbol values fixed height
        self.label_symbol_values_fixed_height = QLabel("Symbol values height")
        self.spinbox_symbol_values_fixed_height = QDoubleSpinBox()
        self.spinbox_symbol_values_fixed_height.setDecimals(2)
        self.spinbox_symbol_values_fixed_height.setRange(-100, 100)
        self.spinbox_symbol_values_fixed_height.valueChanged.connect(self.plot_view.set_symbol_values_height)

        # Symbol values size
        self.label_symbol_values_size = QLabel("Symbol values size")
        self.spinbox_symbol_values_size = QSpinBox()
        self.spinbox_symbol_values_size.setRange(1, 100)
        self.spinbox_symbol_values_size.valueChanged.connect(self.plot_view.set_symbol_values_size)

        self.layout_symbol_values.addRow(self.label_show_symbol_values, self.checkbox_symbol_values)
        self.layout_symbol_values.addRow(self.label_symbol_values_size, self.spinbox_symbol_values_size)
        self.layout_symbol_values.addRow(self.label_symbol_values_position, self.combobox_symbol_values_position)
        self.layout_symbol_values.addRow(self.label_symbol_values_fixed_height, self.spinbox_symbol_values_fixed_height)
        self.widget_symbol_values.setLayout(self.layout_symbol_values)

        button_default_settings = QPushButton("Default settings")
        button_default_settings.clicked.connect(self.plot_view.load_default_settings)

        self.layout.addWidget(self.label_datalines)
        self.layout.addWidget(self.widget_datalines)
        self.layout.addWidget(self.checkboxes_datalines_widget)
        self.layout.addWidget(ViewUtils.line_h())
        self.layout.addWidget(self.label_landmarks)
        self.layout.addWidget(self.widget_landmarks)
        self.layout.addWidget(self.checkboxes_landmarks_widget)
        self.layout.addWidget(ViewUtils.line_h())
        self.layout.addWidget(self.label_symbol_intervals)
        self.layout.addWidget(self.widget_symbol_intervals)
        self.layout.addWidget(ViewUtils.line_h())
        self.layout.addWidget(self.label_symbol_values)
        self.layout.addWidget(self.widget_symbol_values)
        self.layout.addWidget(ViewUtils.line_h())
        self.layout.addWidget(button_default_settings)

        self.setLayout(self.layout)

    def add_datalines(self, receiver_info):
        """
        Add settings for datalines.
        :param receiver_info: Information about receiver.
        """
        # Helper functions necessary for connecting multiple widgets to the same function
        def generate_lambda_checkbox(i, j, o):
            return lambda: self.plot_view.toggle_sensor_dataline(i, j, o)

        def generate_lambda_receiver_checkbox(i, o):
            return lambda: self.plot_view.toggle_all_sensor_datalines(i, o)

        def generate_lambda_button(i, j):
            return lambda: self.plot_view.set_color(i, j)

        def generate_lambda_combobox(i, j, o):
            return lambda: self.plot_view.set_style(i, j, o)

        for receiver_index in range(receiver_info['num']):
            name, sensor_names = receiver_info['names'][receiver_index], receiver_info['sensor_names'][receiver_index]
            receiver_widget = QWidget()
            receiver_layout = QHBoxLayout()
            checkbox_receiver = QCheckBox(name)
            checkbox_receiver.setTristate(True)
            all_, any_ = all(self.plot_view.settings['datalines_active'][receiver_index]), any(self.plot_view.settings['datalines_active'][receiver_index])
            state = 2 if all_ else (1 if any_ else 0)
            checkbox_receiver.setCheckState(Qt.CheckState(state))
            checkbox_receiver.clicked.connect(generate_lambda_receiver_checkbox(receiver_index, checkbox_receiver))
            self.checkboxes_receivers_active.append(checkbox_receiver)
            receiver_layout.addWidget(checkbox_receiver)

            _checkboxes_active = []
            _buttons_color = []
            _comboboxes_style = []
            for sensor_index in range(len(sensor_names)):
                widget_sensor = QWidget()
                layout_sensor = QVBoxLayout()

                # Checkbox for toggling datalines
                checkbox = QCheckBox(sensor_names[sensor_index])
                checkbox.setChecked(self.plot_view.settings['datalines_active'][receiver_index][sensor_index])
                checkbox.clicked.connect(generate_lambda_checkbox(receiver_index, sensor_index, checkbox))
                _checkboxes_active.append(checkbox)

                # Button for selecting color of the datalines
                button_color = QPushButton()
                button_color.setStyleSheet("background-color: " + self.plot_view.settings['datalines_color'][receiver_index][sensor_index])
                button_color.clicked.connect(generate_lambda_button(receiver_index, sensor_index))
                _buttons_color.append(button_color)

                # Combobox for selecting style of the datalines
                combobox = QComboBox()
                combobox.addItems(["SolidLine", "DashLine", "DotLine", "DashDotLine", "DashDotDotLine"])
                combobox.setCurrentText(self.plot_view.settings['datalines_style'][receiver_index][sensor_index])
                combobox.activated.connect(generate_lambda_combobox(receiver_index, sensor_index, combobox))
                _comboboxes_style.append(combobox)

                layout_sensor.addWidget(checkbox)
                layout_sensor.addWidget(button_color)
                layout_sensor.addWidget(combobox)
                widget_sensor.setLayout(layout_sensor)

                receiver_layout.addWidget(widget_sensor)
            self.checkboxes_active.append(_checkboxes_active)
            self.buttons_color.append(_buttons_color)
            self.comboboxes_style.append(_comboboxes_style)

            receiver_widget.setLayout(receiver_layout)
            self.checkboxes_datalines_layout.addWidget(receiver_widget)

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

        all_, any_ = all(self.plot_view.settings['landmarks_active']), any(self.plot_view.settings['landmarks_active'])
        state = 2 if all_ else (1 if any_ else 0)
        self.checkbox_all_landmarks.setCheckState(Qt.CheckState(state))

        num_landmarks = landmark_info['num']
        for landmark_index in range(num_landmarks):
            widget = QWidget()
            layout = QVBoxLayout()

            # Checkbox to toggle landmark
            checkbox = QCheckBox(landmark_info['names'][landmark_index])
            checkbox.setChecked(self.plot_view.settings['landmarks_active'][landmark_index])
            checkbox.clicked.connect(generate_lambda_landmark_toggle(landmark_index, checkbox))
            self.checkboxes_landmarks.append(checkbox)

            # Combobox to select symbol
            combobox = QComboBox()
            combobox.addItems(PlotView.SYMBOLS.keys())
            combobox.setCurrentIndex(list(PlotView.SYMBOLS.values()).index(self.plot_view.settings['landmarks_symbols'][landmark_index]))
            combobox.activated.connect(generate_lambda_landmark_symbol(landmark_index, combobox))
            self.comboboxes_landmarks_symbol.append(combobox)

            # Button for selecting color of the landmark
            button_color = QPushButton()
            button_color.setStyleSheet("background-color: " + self.plot_view.settings['landmarks_color'][landmark_index])
            button_color.clicked.connect(generate_lambda_button(landmark_index))
            self.buttons_landmarks_color.append(button_color)

            layout.addWidget(checkbox)
            layout.addWidget(combobox)
            layout.addWidget(button_color)

            widget.setLayout(layout)
            self.checkboxes_landmarks_layout.addWidget(widget)
        self.checkboxes_landmarks_layout.addStretch(1)

    def decoder_added(self):
        """
        Edit settings dialog entries accordingly when a decoder is added.
        """
        self.spinbox_datalines_width.setValue(self.plot_view.settings['datalines_width'])
        self.spinbox_landmarks_size.setValue(self.plot_view.settings['landmarks_size'])
        self.spinbox_symbol_intervals_width.setValue(self.plot_view.settings['symbol_intervals_width'])
        self.button_symbol_intervals_color.setStyleSheet("background-color: " + self.plot_view.settings['symbol_intervals_color'])
        self.combobox_symbol_values_position.setCurrentText(self.plot_view.settings['symbol_values_position'])
        self.spinbox_symbol_values_size.setValue(self.plot_view.settings['symbol_values_size'])
        self.spinbox_symbol_values_fixed_height.setValue(self.plot_view.settings['symbol_values_fixed_height'])
        if self.plot_view.settings['symbol_values_position'] == "Fixed":
            self.spinbox_symbol_values_fixed_height.setEnabled(True)
        else:
            self.spinbox_symbol_values_fixed_height.setEnabled(False)

    def decoder_removed(self):
        """
        Reset everything after decoder has been removed.
        """
        self.checkboxes_receivers_active = []
        self.checkboxes_active = []
        self.buttons_color = []
        self.comboboxes_style = []

        # https://stackoverflow.com/questions/4528347/clear-all-widgets-in-a-layout-in-pyqt
        for i in reversed(range(self.checkboxes_datalines_layout.count())):
            self.checkboxes_datalines_layout.removeWidget(self.checkboxes_datalines_layout.itemAt(i).widget())

        self.checkboxes_landmarks = []
        self.comboboxes_landmarks_symbol = []

        for i in reversed(range(self.checkboxes_landmarks_layout.count())):
            self.checkboxes_landmarks_layout.removeWidget(self.checkboxes_landmarks_layout.itemAt(i).widget())

        self.hide()

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
        for sensor_index in range(len(self.checkboxes_active[receiver_index])):
            self.checkboxes_active[receiver_index][sensor_index].setChecked(state)