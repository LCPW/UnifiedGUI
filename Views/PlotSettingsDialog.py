from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from Views import PlotView
from Views import Utils


class PlotSettingsDialog(QDialog):
    def __init__(self, plot_view):
        super().__init__()

        self.plot_view = plot_view

        self.setWindowTitle("Plot Settings")
        self.setWindowIcon(Utils.get_icon('settings'))
        self.setModal(False)

        self.layout = QVBoxLayout()

        self.checkboxes_receivers_active = []
        self.checkboxes_active = []
        self.buttons_color = []
        self.comboboxes_style = []
        self.checkboxes_landmarks = []
        self.comboboxes_landmarks_symbol = []

        self.checkboxes_datalines_widget = QWidget()
        self.checkboxes_datalines_layout = QHBoxLayout()
        self.checkboxes_datalines_widget.setLayout(self.checkboxes_datalines_layout)

        self.checkbox_all_landmarks = QCheckBox("Show landmarks")
        self.checkbox_all_landmarks.setTristate(True)
        self.checkbox_all_landmarks.setChecked(True)
        self.checkbox_all_landmarks.clicked.connect(self.plot_view.toggle_all_landmarks)

        self.checkboxes_landmarks_widget = QWidget()
        self.checkboxes_landmarks_layout = QHBoxLayout()
        self.checkboxes_landmarks_widget.setLayout(self.checkboxes_landmarks_layout)

        self.checkbox_symbol_intervals = QCheckBox("Show symbol intervals")
        self.checkbox_symbol_intervals.setChecked(True)
        self.checkbox_symbol_intervals.clicked.connect(self.plot_view.toggle_symbol_intervals)

        self.checkbox_symbol_values = QCheckBox("Show symbol values")
        self.checkbox_symbol_values.setChecked(True)
        self.checkbox_symbol_values.clicked.connect(self.plot_view.toggle_symbol_values)

        def line():
            line_ = QFrame()
            line_.setFrameShape(QFrame.HLine)
            line_.setFrameShadow(QFrame.Sunken)
            return line_

        self.layout.addWidget(self.checkboxes_datalines_widget)
        self.layout.addWidget(line())
        self.layout.addWidget(self.checkbox_all_landmarks)
        self.layout.addWidget(self.checkboxes_landmarks_widget)
        self.layout.addWidget(line())
        self.layout.addWidget(self.checkbox_symbol_intervals)
        self.layout.addWidget(line())
        self.layout.addWidget(self.checkbox_symbol_values)

        self.setLayout(self.layout)

    def add_datalines(self, receiver_info):
        # Helper function for passing a reference of the clicked checkbox to the handler function
        def generate_lambda_checkbox(i, j, o):
            return lambda: self.plot_view.toggle_sensor_dataline(i, j, o)

        def generate_lambda_receiver_checkbox(i, o):
            return lambda: self.plot_view.toggle_all_sensor_datalines(i, o)

        def generate_lambda_button(i, j):
            return lambda: self.plot_view.set_color(i, j)

        def generate_lambda_combobox(i, j, o):
            return lambda: self.plot_view.set_style(i, j, o)

        for receiver_index in range(len(receiver_info)):
            name, sensor_names = receiver_info[receiver_index]['name'], receiver_info[receiver_index]['sensor_names']
            widget = QWidget()
            layout = QVBoxLayout()
            checkbox = QCheckBox(name)
            checkbox.setTristate(True)
            checkbox.setChecked(True)
            checkbox.clicked.connect(generate_lambda_receiver_checkbox(receiver_index, checkbox))
            self.checkboxes_receivers_active.append(checkbox)
            layout.addWidget(checkbox)

            _checkboxes_active = []
            _buttons_color = []
            _comboboxes_style = []
            for sensor_index in range(len(sensor_names)):
                checkbox = QCheckBox(sensor_names[sensor_index])
                checkbox.setChecked(True)
                checkbox.clicked.connect(generate_lambda_checkbox(receiver_index, sensor_index, checkbox))
                _checkboxes_active.append(checkbox)
                button_color = QPushButton()
                button_color.setStyleSheet("background-color: " + self.plot_view.settings['datalines_pens'][receiver_index][sensor_index].color().name())
                button_color.clicked.connect(generate_lambda_button(receiver_index, sensor_index))
                _buttons_color.append(button_color)
                combobox = QComboBox()
                combobox.addItems(["SolidLine", "DashLine", "DotLine", "DashDotLine", "DashDotDotLine"])
                combobox.activated.connect(generate_lambda_combobox(receiver_index, sensor_index, combobox))
                _comboboxes_style.append(combobox)
                layout.addWidget(checkbox)
                layout.addWidget(button_color)
                layout.addWidget(combobox)
            self.checkboxes_active.append(_checkboxes_active)
            self.buttons_color.append(_buttons_color)
            self.comboboxes_style.append(_comboboxes_style)

            widget.setLayout(layout)
            self.checkboxes_datalines_layout.addWidget(widget)

    def add_landmarks(self, landmark_info):
        def generate_lambda_landmark_toggle(i, o):
            return lambda: self.plot_view.toggle_landmark(i, o)

        def generate_lambda_landmark_symbol(i, o):
            return lambda: self.plot_view.set_landmark_symbol(i, o)

        num_landmarks = landmark_info['num']
        for landmark_index in range(num_landmarks):
            widget = QWidget()
            layout = QVBoxLayout()

            # Checkbox to toggle dataline
            checkbox = QCheckBox(landmark_info['names'][landmark_index])
            checkbox.setChecked(True)
            checkbox.clicked.connect(generate_lambda_landmark_toggle(landmark_index, checkbox))
            self.checkboxes_landmarks.append(checkbox)

            # Combobox to select symbol
            combobox = QComboBox()
            combobox.addItems(PlotView.SYMBOLS.keys())
            combobox.setCurrentIndex(list(PlotView.SYMBOLS.values()).index(landmark_info['symbols'][landmark_index]))
            combobox.activated.connect(generate_lambda_landmark_symbol(landmark_index, combobox))
            self.comboboxes_landmarks_symbol.append(combobox)

            layout.addWidget(checkbox)
            layout.addWidget(combobox)

            widget.setLayout(layout)
            self.checkboxes_landmarks_layout.addWidget(widget)
        self.checkboxes_landmarks_layout.addStretch(1)

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