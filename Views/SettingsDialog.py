from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from Utils import ViewUtils


class SettingsDialog(QDialog):
    def __init__(self, menubar):
        super().__init__()

        self.menubar = menubar

        self.setWindowTitle("Settings")
        self.setWindowIcon(ViewUtils.get_icon('settings'))

        layout = QHBoxLayout()
        self.tabs = QTabWidget()

        self.widget_general = QWidget()
        self.layout_general = QFormLayout()

        # self.layout_general.addRow(QLabel("1"), QLabel("2"))

        self.widget_general.setLayout(self.layout_general)

        self.tabs.addTab(self.widget_general, "General")

        layout.addWidget(self.tabs)
        self.setLayout(layout)