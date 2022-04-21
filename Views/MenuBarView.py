from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
import subprocess
import os

from Utils import ViewUtils


class MenuBarView(QMenuBar):
    def __init__(self, view):
        self.view = view
        super(MenuBarView, self).__init__()

        menu_file = self.addMenu("File")
        menu_file.addAction("Exit", self.view.close)

        menu_log = self.addMenu("Log")
        self.action_log_toggle = QAction("Show Log", self)
        self.action_log_toggle.triggered.connect(self.view.toggle_log)
        self.action_log_toggle.setCheckable(True)
        self.action_log_toggle.setChecked(True)
        menu_log.addAction(self.action_log_toggle)

        menu_settings = self.addMenu("Settings")

        menu_help = self.addMenu("Help")
        action_help = QAction(text="Open Documentation (PDF)", parent=self, icon=ViewUtils.get_icon('pdf'))
        action_help.triggered.connect(self.show_documentation)
        action_help_release_notes = QAction(text="Open Release Notes (PDF)", parent=self, icon=ViewUtils.get_icon('pdf'))
        action_help_release_notes.triggered.connect(self.show_release_notes)
        menu_help.addAction(action_help)
        menu_help.addAction(action_help_release_notes)

    @staticmethod
    def show_documentation():
        path = os.path.join('.', 'Docs', 'UnifiedGUI.pdf')
        p = subprocess.Popen([path], shell=True)
        #if p.returncode != 0:
            #Logging.error("Failed to load documentation pdf. Manually open the document (./Docs/UnifiedGUI.pdf)")

    @staticmethod
    def show_release_notes():
        path = os.path.join('.', 'Docs', 'UnifiedGUI_ReleaseNotes.pdf')
        p = subprocess.Popen([path], shell=True)
