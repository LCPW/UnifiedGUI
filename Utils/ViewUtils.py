from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
import os

from PyQt5.QtWidgets import QMessageBox, QStyle

from Views import ParameterDialog

ICON_PATH = os.path.join('.', 'Views', 'Icons')


def get_icon(name):
    """
    Produces a QIcon.
    :param name: Icon name (without filename extension).
    :return: A new QIcon.
    """
    return QIcon(os.path.join(ICON_PATH, name) + '.png')


def get_parameter_values(parameters, current_values=None):
    """
    Executes a parameter dialog.
    :param parameters: Information about parameters.
    :param current_values: Default values for the parameters.
    :return: A tuple consisting of the return code and the parameter values themself.
    """
    parameter_dialog = ParameterDialog.ParameterDialog(parameters, current_values=current_values)
    return parameter_dialog.exec(), parameter_dialog.values


def get_pixmap(name, scale=(24, 24)):
    """
    Produces a QPixmap.
    :param name: Icon name (without filename extension).
    :param scale: Desired size in pixels, default is 24x24.
    :return: A new QPixmap.
    """
    return QPixmap(os.path.join('.', 'Views', 'Icons', name) + '.png').scaled(scale[0], scale[1])


def window_height():
    """
    Returns the screen height.
    :return: The screen height.
    """
    return QApplication.primaryScreen().size().height()


def window_width():
    """
    Returns the screen width.
    :return: The screen width.
    """
    return QApplication.primaryScreen().size().width()


def line_h():
    """
    Produces a horizontal line.
    :return: A new horizontal line.
    """
    line = QFrame()
    line.setFrameShape(QFrame.HLine)
    line.setFrameShadow(QFrame.Sunken)
    return line


def line_v():
    """
    Produces a vertical line.
    :return: A new vertical line.
    """
    line = QFrame()
    line.setFrameShape(QFrame.VLine)
    line.setFrameShadow(QFrame.Sunken)
    return line


def message_box_question(style, title, text, informative_text=None):
    """
    Creates a question message box.
    :param style: QStyle object.
    :param title: Message box title.
    :param text: Message box text.
    :param informative_text: Message box further text (optional).
    :return: Whether the user has clicked 'Yes'.
    """
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


def message_box_warning(style, title, text, informative_text=None):
    """
    Creates a warning message box.
    :param style: QStyle object.
    :param title: Message box title.
    :param text: Message box text.
    :param informative_text: Message box further text (optional).
    :return: Whether the user has clicked 'Yes'.
    """
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