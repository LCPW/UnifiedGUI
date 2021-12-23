from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *


class StatusBarView(QStatusBar):
    def __init__(self):
        super(StatusBarView, self).__init__()

        self.label_fps = QLabel("")
        self.addWidget(self.label_fps)

    def set_fps(self, fps):
        fps_string = str(fps) if fps <= 120 else ">120"
        self.label_fps.setText("FPS: " + str(fps_string))
