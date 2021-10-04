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

        encoder_view = EncoderView.EncoderView()
        self.data = DataView.DataView()
        decoder = DecoderView.DecoderView(self)

        splitter.addWidget(encoder_view)
        splitter.addWidget(self.data)
        splitter.addWidget(decoder)

        layout.addWidget(splitter)
        central_widget.setLayout(layout)

        self.setCentralWidget(central_widget)

    def view_add_decoder(self, num_receivers):
        self.data.add_receivers(num_receivers)

    def update_values(self, vals):
        if vals is not None:
            self.data.update_values(vals)

    def add_encoder(self, encoder_type):
        self.controller.add_encoder(encoder_type)

    def remove_encoder(self):
        self.controller.remove_encoder()

    def add_decoder(self, decoder_type):
        self.controller.add_decoder(decoder_type)

    def remove_decoder(self):
        self.controller.remove_decoder()

    def start_decoder(self):
        self.controller.start_decoder()

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


