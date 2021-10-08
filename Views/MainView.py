from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
import sys
from Views import EncoderView, DecoderView, DataView, ToolbarView


class MainView(QMainWindow):
    def __init__(self, controller):
        super(MainView, self).__init__()

        self.controller = controller

        # Window Title and icon
        self.setWindowTitle("UnifiedGUI")
        icon_window = self.style().standardIcon(getattr(QStyle, 'SP_TitleBarMenuButton'))
        self.setWindowIcon(icon_window)

        # Set window size to maximum
        self.setWindowState(Qt.WindowMaximized)

        self.toolbar = ToolbarView.ToolbarView()
        self.addToolBar(self.toolbar)

        central_widget = QWidget(self)

        layout = QHBoxLayout()
        splitter = QSplitter(Qt.Horizontal)

        self.encoder_view = EncoderView.EncoderView()
        self.data_view = DataView.DataView()
        self.decoder_view = DecoderView.DecoderView(self)

        splitter.addWidget(self.encoder_view)
        splitter.addWidget(self.data_view)
        splitter.addWidget(self.decoder_view)

        layout.addWidget(splitter)
        central_widget.setLayout(layout)

        self.setCentralWidget(central_widget)

        self.timer = QTimer()
        # TODO
        self.timer.setInterval(20)
        self.timer.timeout.connect(self.update)
        self.timer.start()

    def update(self):
        self.data_view.update()

    def decoder_added(self, receiver_info):
        # TODO: Update decoder view
        # Update data view
        self.data_view.add_receivers(receiver_info)

    def decoder_removed(self):
        # TODO
        pass

    def update_values(self, vals):
        if vals is not None:
            self.data_view.update_values(vals)

    def closeEvent(self, close_event: QCloseEvent):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Question)
        icon_msg = self.style().standardIcon(getattr(QStyle, 'SP_MessageBoxQuestion'))
        msg.setWindowIcon(icon_msg)
        msg.setText("Are you sure you want to exit?")
        msg.setWindowTitle("Exit?")
        msg.setStandardButtons(QMessageBox.Yes | QMessageBox.Cancel)
        ret = msg.exec()
        if ret == QMessageBox.Yes:
            self.controller.close()
            close_event.accept()
        else:
            close_event.ignore()