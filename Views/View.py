from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
import sys
import numpy as np
import time

from Views import EncoderView, DecoderView, DataView, MenuBarView, ToolbarView, StatusBarView, ParameterDialog, MessageBoxes, LogView


class View(QMainWindow):
    def __init__(self, controller):
        super(View, self).__init__()

        self.controller = controller
        self.parameter_dialog = None

        # Window Title and icon
        self.setWindowTitle("UnifiedGUI")
        icon_window = self.style().standardIcon(getattr(QStyle, 'SP_TitleBarMenuButton'))
        self.setWindowIcon(icon_window)

        # Set window size to maximum
        self.setWindowState(Qt.WindowMaximized)

        # Menu bar
        self.menu_bar = MenuBarView.MenuBarView(self)
        self.setMenuBar(self.menu_bar)

        self.toolbar = ToolbarView.ToolbarView()
        self.addToolBar(self.toolbar)

        self.status_bar = StatusBarView.StatusBarView()
        self.setStatusBar(self.status_bar)

        central_widget = QWidget(self)

        layout = QHBoxLayout()
        splitter = QSplitter(Qt.Horizontal)

        self.encoder_view = EncoderView.EncoderView()
        self.data_view = DataView.DataView(self)
        self.decoder_view = DecoderView.DecoderView(self)

        splitter.addWidget(self.encoder_view)
        splitter.addWidget(self.data_view)
        splitter.addWidget(self.decoder_view)
        splitter.setStretchFactor(0, 25)
        splitter.setStretchFactor(1, 50)
        splitter.setStretchFactor(2, 25)

        layout.addWidget(splitter)
        central_widget.setLayout(layout)

        self.setCentralWidget(central_widget)

        dock = LogView.LogView()

        self.addDockWidget(Qt.BottomDockWidgetArea, dock)

        self.timer = QTimer()
        # A QTimer with a timeout of 0 will time out as soon as possible.
        self.timer.setInterval(0)
        self.timer.timeout.connect(self.update_)
        self.timer.start()

        self.last_time = time.time()
        self.last_fps = []

    def update_(self):
        decoded = self.controller.get_decoded()
        if decoded is not None:
            received, landmarks, symbol_intervals, symbol_values, sequence = decoded['received'], decoded['landmarks'], decoded['symbol_intervals'], decoded['symbol_values'], decoded['sequence']

            self.data_view.update_values(received)
            self.data_view.update_landmarks(landmarks)
            self.data_view.update_symbol_intervals(symbol_intervals)
            self.data_view.update_symbol_values(symbol_intervals, symbol_values)

            self.decoder_view.update_symbol_values(symbol_values)
            self.decoder_view.update_sequence(sequence)

        # TODO: FPS calculation
        time_ = time.time()
        time_difference = time_ - self.last_time + 0.0000001
        fps = 1 / time_difference
        self.last_fps.append(fps)
        if len(self.last_fps) == 10:
            fps_avg = int(np.round(sum(self.last_fps) / len(self.last_fps)))
            self.status_bar.set_fps(fps_avg)
            self.last_fps = []
        self.last_time = time_

    def decoder_added(self, decoder_type, receiver_info, landmark_info, parameter_values):
        # Update decoder view
        self.decoder_view.decoder_added(decoder_type, parameter_values)

        # Update data view
        self.data_view.decoder_added(receiver_info, landmark_info)

    def decoder_removed(self):
        self.data_view.decoder_removed()
        self.decoder_view.decoder_removed()

    def get_parameter_values(self, parameters, current_values=None):
        self.parameter_dialog = ParameterDialog.ParameterDialog(parameters, current_values=current_values)
        return self.parameter_dialog.exec()

    def closeEvent(self, close_event: QCloseEvent):
        if MessageBoxes.question(self.style(), "Exit?", "Are you sure you want to exit?"):
            self.controller.close()
            close_event.accept()
        else:
            close_event.ignore()