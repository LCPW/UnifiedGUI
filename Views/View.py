from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
import sys
import numpy as np
import time

import Utils.ViewUtils
from Views import EncoderView, DecoderView, DataView, MenuBarView, ToolbarView, StatusBarView, LogView


class View(QMainWindow):
    def __init__(self, controller):
        """
        Initializes the main window.
        :param controller: Controller object.
        """
        super(View, self).__init__()

        self.controller = controller

        # Window Title and icon
        self.setWindowTitle("UnifiedGUI")
        icon_window = self.style().standardIcon(getattr(QStyle, 'SP_TitleBarMenuButton'))
        self.setWindowIcon(icon_window)

        # Set window size to maximum
        self.setWindowState(Qt.WindowMaximized)

        # Menu bar
        self.menu_bar = MenuBarView.MenuBarView(self)
        self.setMenuBar(self.menu_bar)

        # Tool bar
        self.toolbar = ToolbarView.ToolbarView()
        # self.addToolBar(self.toolbar)

        # Status bar
        self.status_bar = StatusBarView.StatusBarView()
        self.setStatusBar(self.status_bar)

        # Log widget
        self.log_view = LogView.LogView(self)
        self.addDockWidget(Qt.BottomDockWidgetArea, self.log_view)

        central_widget = QWidget(self)
        layout = QHBoxLayout()
        splitter = QSplitter(Qt.Horizontal)

        self.encoder_view = EncoderView.EncoderView(self)
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

        self.timer = QTimer()
        # A QTimer with a timeout of 0 will time out as soon as possible.
        self.timer.setInterval(0)
        self.timer.timeout.connect(self.update_)
        self.timer.start()

        self.last_time = time.time()
        self.last_fps = []

    def closeEvent(self, close_event: QCloseEvent):
        """
        Re-defines the close event by asking the user for confirmation before actually closing.
        :param close_event: Close event.
        """
        if Utils.ViewUtils.message_box_question(self.style(), "Exit?", "Are you sure you want to exit?"):
            self.controller.close()
            self.data_view.tab_plot.plot_settings_dialog.close()
            close_event.accept()
        else:
            close_event.ignore()

    def decoder_added(self, decoder_info):
        """
        Do stuff when a decoder is added.
        :param decoder_info: Information about decoder.
        """
        self.data_view.decoder_added(decoder_info)
        self.decoder_view.decoder_added(decoder_info)
        self.update_window_title()

    def decoder_clear(self):
        """
        Clears stuff from decoder view and data view.
        """
        self.data_view.decoder_clear()
        self.decoder_view.decoder_clear()

    def decoder_removed(self):
        """
        Do stuff when a decoder is removed.
        """
        self.data_view.decoder_removed()
        self.decoder_view.decoder_removed()
        self.update_window_title()

    def encoder_added(self, encoder_info):
        """
        Do stuff when an encoder is added.
        :param encoder_info: Information about encoder.
        """
        self.encoder_view.encoder_added(encoder_info)
        self.update_window_title()

    def encoder_removed(self):
        """
        Do stuff when an encoder is removed.
        """
        self.encoder_view.encoder_removed()
        self.update_window_title()

    def toggle_log(self, state):
        """
        Toggles the log wiget.
        This is executed if the user clicks on the X button on the log window or via the menu ba.
        :param state: True -> Show, False -> Hide
        """
        if state:
            self.log_view.show()
            self.menu_bar.action_log_toggle.setChecked(True)
        else:
            self.log_view.hide()
            self.menu_bar.action_log_toggle.setChecked(False)

    def update_(self):
        """
        Updates the view.
        This function is repeatedly called whenever the QTimer times out.
        """
        decoded = self.controller.get_decoded()
        if decoded is not None:
            self.data_view.update_(decoded)
            self.decoder_view.update_(decoded)

        encoder_info = self.controller.get_encoder_info()
        if encoder_info is not None:
            self.encoder_view.update_(encoder_info)

        time_ = time.time()
        time_difference = time_ - self.last_time + sys.float_info.epsilon
        fps = 1 / time_difference
        self.last_fps.append(fps)
        if len(self.last_fps) == 10:
            fps_avg = int(np.mean(self.last_fps))
            self.status_bar.set_fps(fps_avg)
            self.last_fps = []
        self.last_time = time_

    def update_window_title(self):
        """
        Updates the window title based on currently active encoders/decoders.
        """
        title = "UnifiedGUI"
        decoder_info, encoder_info = self.controller.get_decoder_info(), self.controller.get_encoder_info()
        if encoder_info is not None and decoder_info is not None:
            title += " [Encoder: " + encoder_info['type']
            title += " | Decoder:" + decoder_info['type'] + "]"
        elif encoder_info is not None:
            title += " [Encoder: " + encoder_info['type'] + "]"
        elif decoder_info is not None:
            title += " [Decoder: " + decoder_info['type'] + "]"
        self.setWindowTitle(title)