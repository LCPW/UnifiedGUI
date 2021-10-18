from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *


class PlotSettingsDialog(QDialog):
    def __init__(self, plot_view):
        super().__init__()

        self.plot_view = plot_view

        self.setWindowTitle("Plot Settings")
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

    def add_receivers(self, receiver_info):
        # Helper function for passing a reference of the clicked checkbox to the handler function
        def generate_lambda(i_, j_):
            return lambda: self.toggle_checkbox(i_, j_)

        def generate_lambda2(i_):
            return lambda: self.plot_view.toggle_receiver_checkbox(i_)

        def generate_lambda3(i_, j_):
            return lambda: self.plot_view.set_color(i_, j_)

        def generate_lambda4(i_, j_):
            return lambda: self.plot_view.set_style(i_, j_)

        for i in range(len(receiver_info)):
            description, sensor_descriptions = receiver_info[i]['description'], receiver_info[i]['sensor_descriptions']
            widget = QWidget()
            layout = QVBoxLayout()
            checkbox = QCheckBox(description)
            checkbox.setTristate(True)
            checkbox.setChecked(True)
            # TODO: Generate Lambda rename
            checkbox.clicked.connect(generate_lambda2(i))
            self.checkboxes_receivers_active.append(checkbox)
            layout.addWidget(checkbox)

            _checkboxes_active = []
            _buttons_color = []
            _comboboxes_style = []
            for j in range(len(sensor_descriptions)):
                checkbox = QCheckBox(sensor_descriptions[j])
                checkbox.setChecked(True)
                checkbox.clicked.connect(generate_lambda(i, j))
                _checkboxes_active.append(checkbox)
                button_color = QPushButton()
                button_color.setStyleSheet("background-color: " + self.plot_view.settings['pens'][i][j].color().name())
                button_color.clicked.connect(generate_lambda3(i, j))
                _buttons_color.append(button_color)
                combobox = QComboBox()
                combobox.addItems(["SolidLine", "DashedLine", "DotLine", "DashDotLine", "DashDotDotLine"])
                combobox.activated.connect(generate_lambda4(i, j))
                _comboboxes_style.append(combobox)
                layout.addWidget(checkbox)
                layout.addWidget(button_color)
                layout.addWidget(combobox)
            self.checkboxes_active.append(_checkboxes_active)
            self.buttons_color.append(_buttons_color)
            self.comboboxes_style.append(_comboboxes_style)

            widget.setLayout(layout)
            self.checkbox_layout.addWidget(widget)

    def toggle_checkbox(self, receiver_index, sensor_index):
        # TODO
        # Toggle selected checkbox
        # Check if the tri-state checkbox needs to be updated
        # Update settings
        self.plot_view.toggle_checkbox(receiver_index, sensor_index)
        pass

    def set_receiver_checkboxes(self, receiver_index, state):
        for sensor_index in range(len(self.checkboxes_active[receiver_index])):
            # TODO: Falsch
            # self.plot_view.settings['active_big'][sensor_index] = state
            self.checkboxes_active[receiver_index][sensor_index].setChecked(state)
