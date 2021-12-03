from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
import pyqtgraph as pg
from datetime import datetime
import numpy as np


class PlotWidgetView(pg.PlotWidget):
    def __init__(self, plot_view):
        #super().__init__(axisItems={'bottom': TimeAxisItem(orientation='bottom')})
        super().__init__(axisItems={'bottom': pg.DateAxisItem(orientation='bottom')})

        self.plot_view = plot_view

        # Set background color to white
        self.setBackground('w')

        # Axis labels left and bottom
        self.setLabel('left', "Value")
        self.setLabel('bottom', "Time")

        # Grid
        self.showGrid(x=True, y=True)

        self.data_lines = []
        self.landmarks = []
        self.vertical_lines = []
        self.text_items = []

        self.max_value = 0

        # TODO?
        self.step_size = 1
        # self.setDownsampling(ds=10)

        # TODO: Gut, aber noch besser waere es wenn es der User auswaehlen koennte
        # self.enableAutoRange(axis='y')
        self.setMouseEnabled(x=True, y=False)

        self.legend = pg.LegendItem()
        self.legend.setParentItem(self.getPlotItem())

    def add_datalines(self, receiver_info):
        """
        Adds new datalines to the plot.
        :param receiver_info: Info about receivers (receiver name + sensor desciptions).
        """
        for i in range(len(receiver_info)):
            name, sensor_names = receiver_info[i]['name'], receiver_info[i]['sensor_names']
            data_lines_ = []
            for j in range(len(sensor_names)):
                data_line = self.plot([], [], name=name + ": " + sensor_names[j], pen=self.plot_view.settings['datalines_pens'][i][j])
                data_lines_.append(data_line)
                self.legend.addItem(data_line, data_line.name())
            self.data_lines.append(data_lines_)

    def add_landmarks(self, landmark_info):
        """
        Adds new landmarks to the plot.
        :param landmark_info: Info about landmarks (name + symbols).
        """
        num_landmarks = landmark_info['num']
        for i in range(num_landmarks):
            landmark_ = self.plot([], [], pen=None, symbol=self.plot_view.settings['landmarks_symbols'][i], name=landmark_info['names'][i])
            self.landmarks.append(landmark_)
            self.legend.addItem(landmark_, landmark_.name())

    def clear_dataline(self, receiver_index, sensor_index):
        """
        Clears a given dataline.
        :param receiver_index: Receiver index of the dataline to be cleared.
        :param sensor_index: Sensor index of the dataline to be cleared.
        """
        self.data_lines[receiver_index][sensor_index].clear()
        #self.legend.removeItem(self.data_lines[receiver_index][sensor_index])
        #self.update_legend()
        self.repaint_plot()

    def clear_landmark(self, landmark_index):
        """
        Clears  a given landmark.
        :param landmark_index: Index of the landmark to be cleared.
        """
        self.landmarks[landmark_index].clear()
        #self.legend.removeItem(self.landmarks[landmark_index])
        #self.update_legend()
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
        """
        # Other way possible? update, repaint, resize, QApplication.processEvents do not work...
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
        self.max_value = 0
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
        pen = self.plot_view.settings['datalines_pens'][receiver_index][sensor_index]
        self.data_lines[receiver_index][sensor_index].setPen(pen)

    def update_datalines(self, vals):
        """
        Updates the datalines with new values from the decoder.
        :param vals: Measurement values from the receivers.
        """
        timestamps, values = vals['timestamps'], vals['values']
        for receiver_index in range(len(values)):
            if timestamps[receiver_index] is not None:
                for sensor_index in range(values[receiver_index].shape[1]):
                    if self.plot_view.settings['datalines_active'][receiver_index][sensor_index]:
                        x = timestamps[receiver_index]
                        y = values[receiver_index][:, sensor_index]
                        length_ = min(len(x), len(y))
                        x, y = x[:length_], y[:length_]
                        self.data_lines[receiver_index][sensor_index].setData(x[::self.step_size], y[::self.step_size])

        # TODO: ?
        try:
            self.max_value = max([np.max(a) for a in values])
        except:
            pass
        self.last_vals = vals

    def update_landmarks(self, landmarks):
        """
        Updates the landmarks with new values from the decoder.
        :param landmarks: Landmark coordinates.
        """
        for i in range(len(landmarks)):
            if landmarks[i] is not None and self.plot_view.settings['landmarks_active'][i]:
                x, y = landmarks[i]['x'], landmarks[i]['y']
                self.landmarks[i].setData(x, y)
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
                vertical = pg.InfiniteLine(pos=timestamp, angle=90, movable=False, pen=self.plot_view.settings['symbol_intervals_pen'])
                self.addItem(vertical)
                self.vertical_lines.append(vertical)

        self.last_symbol_intervals = symbol_intervals

    def update_symbol_values(self, symbol_intervals, symbol_values):
        """
        Updates the symbol values with new values from the decoder.
        :param symbol_intervals: Symbol interval positions (relevant for the position of the symbol values).
        :param symbol_values: Symbol values.
        """
        # This is necessary (for now), because symbol_values/symbol_intervals are not updated atomically
        symbol_values = symbol_values[:len(symbol_intervals) - 1]

        if self.plot_view.settings['symbol_values']:
            for i in range(len(self.text_items), len(symbol_values)):
                x_pos = 0.5 * (symbol_intervals[i] + symbol_intervals[i+1])
                text = pg.TextItem(str(symbol_values[i]), color='k')
                text.setPos(x_pos, self.plot_view.settings['symbol_values_height_factor'] * self.max_value)
                self.addItem(text)
                self.text_items.append(text)
        self.last_symbol_values = symbol_values


# class TimeAxisItem(pg.AxisItem):
#     """
#     Converts the timestamps from a float to a human-readable format for the x-axis ticks.
#     """
#     def tickStrings(self, values, scale, spacing):
#         try:
#             x = [datetime.fromtimestamp(value) for value in values]
#             # x = [datetime.time(value) for value in values]
#         # This catches the case that negative values can not be converted into timestamps
#         except OSError:
#             x = ['undefined'] * len(values)
#         return x