from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *


class PlotSettingsDialog(QDialog):
    def __init__(self, plot_view):
        super().__init__()

        self.plot_view = plot_view

        self.setWindowTitle("Plot Settings")
        self.setWindowIcon(QIcon('./Views/Icons/settings.png'))
        self.setModal(False)

        self.layout = QVBoxLayout()

        self.checkboxes_receivers_active = []
        self.checkboxes_active = []
        self.buttons_color = []
        self.comboboxes_style = []

        self.checkbox_widget = QWidget()
        self.checkbox_layout = QHBoxLayout()
        self.checkbox_widget.setLayout(self.checkbox_layout)
        self.layout.addWidget(self.checkbox_widget)

        self.setLayout(self.layout)

    def add_datalines(self, receiver_info):
        # Helper function for passing a reference of the clicked checkbox to the handler function
        def generate_lambda_checkbox(i, j):
            return lambda: self.plot_view.toggle_checkbox(i, j)

        def generate_lambda_receiver_checkbox(i):
            return lambda: self.plot_view.toggle_receiver_checkbox(i)

        def generate_lambda_button(i, j):
            return lambda: self.plot_view.set_color(i, j)

        def generate_lambda_combobox(i, j):
            return lambda: self.plot_view.set_style(i, j)

        for receiver_index in range(len(receiver_info)):
            description, sensor_descriptions = receiver_info[receiver_index]['description'], receiver_info[receiver_index]['sensor_descriptions']
            widget = QWidget()
            layout = QVBoxLayout()
            checkbox = QCheckBox(description)
            checkbox.setTristate(True)
            checkbox.setChecked(True)
            checkbox.clicked.connect(generate_lambda_receiver_checkbox(receiver_index))
            self.checkboxes_receivers_active.append(checkbox)
            layout.addWidget(checkbox)

            _checkboxes_active = []
            _buttons_color = []
            _comboboxes_style = []
            for sensor_index in range(len(sensor_descriptions)):
                checkbox = QCheckBox(sensor_descriptions[sensor_index])
                checkbox.setChecked(True)
                checkbox.clicked.connect(generate_lambda_checkbox(receiver_index, sensor_index))
                _checkboxes_active.append(checkbox)
                button_color = QPushButton()
                button_color.setStyleSheet("background-color: " + self.plot_view.settings['pens'][receiver_index][sensor_index].color().name())
                button_color.clicked.connect(generate_lambda_button(receiver_index, sensor_index))
                _buttons_color.append(button_color)
                combobox = QComboBox()
                combobox.addItems(["SolidLine", "DashedLine", "DotLine", "DashDotLine", "DashDotDotLine"])
                combobox.activated.connect(generate_lambda_combobox(receiver_index, sensor_index))
                _comboboxes_style.append(combobox)
                layout.addWidget(checkbox)
                layout.addWidget(button_color)
                layout.addWidget(combobox)
            self.checkboxes_active.append(_checkboxes_active)
            self.buttons_color.append(_buttons_color)
            self.comboboxes_style.append(_comboboxes_style)

            widget.setLayout(layout)
            self.checkbox_layout.addWidget(widget)
            # self.layout.addWidget(self.checkbox_widget)

    def set_receiver_checkboxes(self, receiver_index, state):
        for sensor_index in range(len(self.checkboxes_active[receiver_index])):
            self.checkboxes_active[receiver_index][sensor_index].setChecked(state)

    def remove_datalines(self):
        self.checkboxes_active = []
        self.buttons_color = []
        self.comboboxes_style = []

        # https://stackoverflow.com/questions/4528347/clear-all-widgets-in-a-layout-in-pyqt
        for i in reversed(range(self.checkbox_layout.count())):
            #self.checkbox_layout.itemAt(i).widget().
            self.checkbox_layout.removeWidget(self.checkbox_layout.itemAt(i).widget())

        self.hide()
