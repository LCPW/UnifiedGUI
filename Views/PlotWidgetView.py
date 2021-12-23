from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
import pyqtgraph as pg
from datetime import datetime
import numpy as np


class PlotWidgetView(pg.PlotWidget):
    def __init__(self, plot_view):
        super().__init__(axisItems={'bottom': pg.DateAxisItem(orientation='bottom')})

        self.plot_view = plot_view

        # Set background color to white
        self.setBackground('w')

        # Axis labels left and bottom
        self.setLabel('left', "Value")
        self.setLabel('bottom', "Time")

        # Grid
        self.showGrid(x=True, y=True)

        self.setMouseEnabled(x=True, y=False)

        # Legend
        self.legend = pg.LegendItem()
        self.legend.setParentItem(self.getPlotItem())

        self.data_lines = []
        self.landmarks = []
        self.text_items = []
        self.vertical_lines = []

    def add_datalines(self, receiver_info):
        """
        Adds new datalines to the plot.
        :param receiver_info: Info about receivers (receiver name + sensor desciptions).
        """
        for receiver_index in range(receiver_info['num']):
            name, sensor_names = receiver_info['names'][receiver_index], receiver_info['sensor_names'][receiver_index]
            data_lines_ = []
            for sensor_index in range(len(sensor_names)):
                pen = pg.mkPen(color=QColor(self.plot_view.settings['datalines_color'][receiver_index][sensor_index]),
                               style=getattr(Qt, self.plot_view.settings['datalines_style'][receiver_index][sensor_index]),
                               width=self.plot_view.settings['datalines_width'])
                data_line = self.plot([], [], name=name + ": " + sensor_names[sensor_index], pen=pen)
                data_lines_.append(data_line)
                self.legend.addItem(data_line, data_line.name())
            self.data_lines.append(data_lines_)

    def add_landmarks(self, landmark_info):
        """
        Adds new landmarks to the plot.
        :param landmark_info: Info about landmarks (name + symbols).
        """
        for landmark_index in range(landmark_info['num']):
            landmark_ = self.plot([], [],
                                  pen=None,
                                  symbol=self.plot_view.settings['landmarks_symbols'][landmark_index],
                                  name=landmark_info['names'][landmark_index],
                                  symbolSize=self.plot_view.settings['landmarks_size'])
            self.landmarks.append(landmark_)
            self.legend.addItem(landmark_, landmark_.name())

    def clear_dataline(self, receiver_index, sensor_index):
        """
        Clears a given dataline.
        :param receiver_index: Receiver index of the dataline to be cleared.
        :param sensor_index: Sensor index of the dataline to be cleared.
        """
        self.data_lines[receiver_index][sensor_index].clear()
        self.repaint_plot()

    def clear_landmark(self, landmark_index):
        """
        Clears  a given landmark.
        :param landmark_index: Index of the landmark to be cleared.
        """
        self.landmarks[landmark_index].clear()
        self.repaint_plot()

    def clear_symbol_intervals(self):
        """
        Clears all symbol intervals (vertical lines) from the plot.
        """
        for i in self.vertical_lines:
            self.removeItem(i)
        self.vertical_lines = []
        self.repaint_plot()

    def clear_symbol_values(self):
        """
        Clears all symbol values from the plot.
        """
        for text_item in self.text_items:
            self.removeItem(text_item)
        self.text_items = []
        self.repaint_plot()

    def repaint_plot(self):
        """
        Repaints the plot.
        In some cases, the plot does not update its content, especially when elements are removed and the plot is not the focused window.
        In this case, the plot has to be updated manually.
        Note:   This is pretty ugly, potentially there is a more elegant way to do this.
                Using update, repaint, resize or QApplication.processEvents did not work.
        """
        self.hide()
        self.show()

    def reset_plot(self):
        """
        Clears the complete plot and resets variables.
        This function should be called before the starting of a decoder.
        """
        for i in range(len(self.data_lines)):
            for j in range(len(self.data_lines[i])):
                self.legend.removeItem(self.data_lines[i][j])
                self.data_lines[i][j].clear()
        self.data_lines = []
        for i in range(len(self.landmarks)):
            self.legend.removeItem(self.landmarks[i])
            self.landmarks[i].clear()
        self.landmarks = []
        self.clear_symbol_intervals()
        self.clear_symbol_values()
        self.repaint_plot()

    def set_landmark_symbol(self, landmark_index):
        """
        Sets a new symbol for a given landmark based on the settings.
        :param landmark_index: Index of the landmark.
        """
        symbol = self.plot_view.settings['landmarks_symbols'][landmark_index]
        self.landmarks[landmark_index].setSymbol(symbol)

    def set_pen(self, receiver_index, sensor_index):
        """
        Sets a new pen for a given dataline based on the settings.
        :param receiver_index: Receiver index of the dataline.
        :param sensor_index: Sensor index of the dataline.
        """
        pen = pg.mkPen(color=self.plot_view.settings['datalines_color'][receiver_index][sensor_index],
                       style=getattr(Qt, self.plot_view.settings['datalines_style'][receiver_index][sensor_index]),
                       width=self.plot_view.settings['datalines_width'])
        self.data_lines[receiver_index][sensor_index].setPen(pen)

    def update_(self, decoded):
        """
        Updates this widget with new information from the decoder.
        :param decoded: Decoder value updates.
        """
        received, landmarks, symbol_intervals, symbol_values, sequence = decoded['received'], decoded['landmarks'], decoded['symbol_intervals'], decoded['symbol_values'], decoded['sequence']
        self.update_datalines(received)
        self.update_landmarks(landmarks)
        self.update_symbol_intervals(symbol_intervals)
        self.update_symbol_values(received, symbol_intervals, symbol_values)

    def update_datalines(self, received):
        """
        Updates the datalines with new values from the decoder.
        :param received: Measurement values from the receivers.
        """
        lengths, timestamps, values = received['lengths'], received['timestamps'], received['values']
        for receiver_index in range(len(values)):
            if lengths[receiver_index] > 0:
                for sensor_index in range(values[receiver_index].shape[1]):
                    if self.plot_view.settings['datalines_active'][receiver_index][sensor_index]:
                        length = lengths[receiver_index]
                        x = timestamps[receiver_index][:length:self.plot_view.settings['step_size']]
                        y = values[receiver_index][:length:self.plot_view.settings['step_size'], sensor_index]
                        self.data_lines[receiver_index][sensor_index].setData(x, y)

    def update_landmarks(self, landmarks):
        """
        Updates the landmarks with new values from the decoder.
        :param landmarks: Landmark coordinates.
        """
        for landmark_index in range(len(landmarks)):
            if landmarks[landmark_index] is not None and self.plot_view.settings['landmarks_active'][landmark_index]:
                x, y = landmarks[landmark_index]['x'], landmarks[landmark_index]['y']
                self.landmarks[landmark_index].setData(x, y)
        self.last_landmarks = landmarks

    def update_legend(self):
        """
        Updates the legend.
        This is usually necessary after a dataline or landmark set has been activated/deactivated.
        """
        self.legend.clear()
        for receiver_index in range(len(self.data_lines)):
            for sensor_index in range(len(self.data_lines[receiver_index])):
                if self.plot_view.settings['datalines_active'][receiver_index][sensor_index]:
                    self.legend.addItem(self.data_lines[receiver_index][sensor_index], self.data_lines[receiver_index][sensor_index].name())
        for landmark_index in range(len(self.landmarks)):
            if self.plot_view.settings['landmarks_active'][landmark_index]:
                self.legend.addItem(self.landmarks[landmark_index], self.landmarks[landmark_index].name())

    def update_symbol_intervals(self, symbol_intervals):
        """
        Updates the symbol intervals (vertical lines) with new values from the decoder.
        :param symbol_intervals: Symbol interval positions.
        """
        if self.plot_view.settings['symbol_intervals']:
            for timestamp in symbol_intervals[len(self.vertical_lines):]:
                pen = pg.mkPen(color=self.plot_view.settings['symbol_intervals_color'],
                               width=self.plot_view.settings['symbol_intervals_width'])
                vertical = pg.InfiniteLine(pos=timestamp, angle=90, movable=False, pen=pen)
                self.addItem(vertical)
                self.vertical_lines.append(vertical)

    def update_symbol_values(self, vals, symbol_intervals, symbol_values):
        """
        Updates the symbol values with new values from the decoder.
        :param vals: Measurement values from the receivers (relevant for the y-position of the symbol values).
        :param symbol_intervals: Symbol interval positions (relevant for the x-position of the symbol values).
        :param symbol_values: Symbol values.
        """
        # This is necessary (for now), because symbol_values/symbol_intervals are not updated atomically
        symbol_values = symbol_values[:len(symbol_intervals) - 1]

        if self.plot_view.settings['symbol_values']:
            for i in range(len(self.text_items), len(symbol_values)):
                x_pos = 0.5 * (symbol_intervals[i] + symbol_intervals[i+1])

                if self.plot_view.settings['symbol_values_position'] in ['above', 'below']:
                    timestamps, values = vals['timestamps'], vals['values']
                    minimum_values, maximum_values = [], []
                    for receiver_index in range(len(timestamps)):
                        left_index = np.argmin(list(map(abs, timestamps[receiver_index] - symbol_intervals[i])))
                        right_index = np.argmin(list(map(abs, timestamps[receiver_index] - symbol_intervals[i+1])))
                        max_tmp = np.max(values[receiver_index][left_index:right_index])
                        min_tmp = np.min(values[receiver_index][left_index:right_index])
                        maximum_values.append(max_tmp)
                        minimum_values.append(min_tmp)
                    maximum_interval_value = max(maximum_values)
                    minimum_interval_value = min(minimum_values)

                    amplitude = maximum_interval_value - minimum_interval_value
                    if self.plot_view.settings['symbol_values_position'] == 'above':
                        y_pos = maximum_interval_value + (0.1 + 0.001 * self.plot_view.settings['symbol_values_size']) * amplitude
                    else:
                        y_pos = minimum_interval_value - (0.1 - 0.001 * self.plot_view.settings['symbol_values_size']) * amplitude
                else:
                    y_pos = self.plot_view.settings['symbol_values_fixed_height']
                text = pg.TextItem(str(symbol_values[i]), color='k')
                text.setPos(x_pos, y_pos)
                text.setFont(QFont('MS Shell Dlg 2', self.plot_view.settings['symbol_values_size']))
                self.addItem(text)
                self.text_items.append(text)