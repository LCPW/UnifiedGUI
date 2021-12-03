from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
import subprocess
import os


class MenuBarView(QMenuBar):
    def __init__(self, view):
        self.view = view
        super(MenuBarView, self).__init__()

        menu_file = self.addMenu("File")
        menu_file.addAction("Exit", self.view.close)

        menu_settings = self.addMenu("Settings")

        menu_help = self.addMenu("Help")
        action_help = QAction(text="Open Documentation (PDF)", parent=self, icon=QIcon('./Views/Icons/pdf.png'))
        action_help.triggered.connect(self.show_help)
        menu_help.addAction(action_help)

    def show_help(self):
        path = os.path.join('.', 'Docs', 'UnifiedGUI.pdf')
        p = subprocess.Popen([path], shell=True)
        #if p.returncode != 0:
            #Logging.error("Failed to load documentation pdf. Manually open the document (./Docs/UnifiedGUI.pdf)")