from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *


def warning(style, title, text, informative_text=None):
    msg = QMessageBox()
    msg.setIcon(QMessageBox.Warning)
    icon_msg = style.standardIcon(getattr(QStyle, 'SP_MessageBoxWarning'))
    msg.setWindowIcon(icon_msg)
    msg.setWindowTitle(title)
    msg.setText(text)
    if informative_text:
        msg.setInformativeText(informative_text)

    msg.setStandardButtons(QMessageBox.Yes | QMessageBox.Cancel)
    ret = msg.exec()
    if ret == QMessageBox.Yes:
        return True
    else:
        return False


def question(style, title, text, informative_text=None):
    msg = QMessageBox()
    msg.setIcon(QMessageBox.Question)
    icon_msg = style.standardIcon(getattr(QStyle, 'SP_MessageBoxQuestion'))
    msg.setWindowIcon(icon_msg)
    msg.setWindowTitle(title)
    msg.setText(text)
    if informative_text:
        msg.setInformativeText(informative_text)
    msg.setStandardButtons(QMessageBox.Yes | QMessageBox.Cancel)
    ret = msg.exec()
    if ret == QMessageBox.Yes:
        return True
    else:
        return False