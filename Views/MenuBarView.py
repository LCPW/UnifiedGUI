from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5 import QtWidgets, QtCore, QtGui, Qt
import subprocess
import os

from Views import SettingsDialog, ExportDialog
from Utils import ViewUtils


class MenuBarView(QMenuBar):
    def __init__(self, view):
        self.view = view
        super(MenuBarView, self).__init__()

        menu_file = self.addMenu("File")
        self.settings_dialog = SettingsDialog.SettingsDialog(self)
        menu_file.addAction(ViewUtils.get_icon('export'), "Export (Plot)", self.export)
        menu_file.addAction(ViewUtils.get_icon('export'), "Export (Custom)", self.export_custom)
        menu_file.addAction(ViewUtils.get_icon('settings'), "Settings", self.show_settings)
        menu_file.addAction("Exit", self.view.close)

        menu_log = self.addMenu("Log")
        self.action_log_toggle = QAction("Show Log", self)
        self.action_log_toggle.triggered.connect(self.view.toggle_log)
        self.action_log_toggle.setCheckable(True)
        self.action_log_toggle.setChecked(True)
        menu_log.addAction(self.action_log_toggle)

        # menu_settings = self.addMenu("Settings")

        menu_help = self.addMenu("Help")
        menu_help.addAction(ViewUtils.get_icon('pdf'), "Open Documentation (PDF)", self.show_documentation)
        menu_help.addAction(ViewUtils.get_icon('pdf'), "Open Release Notes (PDF)", self.show_release_notes)

    @staticmethod
    def show_documentation():
        path = os.path.join('.', 'Docs', 'UnifiedGUI.pdf')
        subprocess.Popen([path], shell=True)

    @staticmethod
    def show_release_notes():
        path = os.path.join('.', 'Docs', 'UnifiedGUI_ReleaseNotes.pdf')
        subprocess.Popen([path], shell=True)

    def show_settings(self):
        self.settings_dialog.show()
        self.settings_dialog.activateWindow()

    def export(self):
        self.view.data_view.tab_plot.plot_widget.export_plot()

    def export_custom(self):
        export_dialog = ExportDialog.ExportDialog(self.view.controller)
        if export_dialog.exec():
            directory = QFileDialog.getExistingDirectory(self, "Select Directory")
            if directory is not None:
                self.view.controller.export_custom(directory, export_dialog.get_data_name(),
                                                   export_dialog.has_selected_encoder_activation(),
                                                   export_dialog.get_additional_data_name())

