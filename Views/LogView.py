from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

import logging
from Views import Utils


class LogTextEdit(QPlainTextEdit, logging.Handler):
    def __init__(self):
        super().__init__()
        self.setReadOnly(True)

    def sizeHint(self):
        width, height = QApplication.primaryScreen().size().width(), QApplication.primaryScreen().size().height()
        return QSize(width, 0.1 * height)

    def emit(self, record):
        msg = self.format(record)
        self.appendPlainText(msg)


class LogView(QDockWidget):
    def __init__(self):
        super(LogView, self).__init__("Log")

        #self.setWindowIcon(view_utils.get_icon('terminal'))
        #self.setTitleBarWidget(QIcon('./Views/Icons/terminal.png'))
        #self.setWindowIcon(QIcon('./Views/Icons/terminal.png'))
        self.setAllowedAreas(Qt.BottomDockWidgetArea | Qt.TopDockWidgetArea)
        self.setFloating(True)

        splitter = QSplitter(Qt.Vertical)

        log_text_edit = LogTextEdit()
        log_text_edit.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
        logging.getLogger().addHandler(log_text_edit)
        logging.getLogger().setLevel(logging.DEBUG)

        splitter.addWidget(log_text_edit)

        #self.DockWidgetVerticalTitleBar = True
        #self.DockWidgetHorizontalTitleBar = True
        self.setWidget(splitter)

        #log_text_edit.emit("Hi")
        #log_text_edit.emit("Hi2")

        #with open('./Views/Style.qss', 'r') as f:
            #QApplication.instance().setStyleSheet(f.read())