from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

import os

ICON_PATH = os.path.join('.', 'Views', 'Icons')


def get_icon(name):
    return QIcon(os.path.join(ICON_PATH, name) + '.png')


def hline():
    line_ = QFrame()
    line_.setFrameShape(QFrame.HLine)
    line_.setFrameShadow(QFrame.Sunken)
    return line_


def vline():
    line_ = QFrame()
    line_.setFrameShape(QFrame.VLine)
    line_.setFrameShadow(QFrame.Sunken)
    return line_