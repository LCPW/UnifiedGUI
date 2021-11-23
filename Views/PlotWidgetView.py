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

        # TODO: Refactor this to avoid data duplication
        self.last_vals = None
        self.last_symbol_intervals = None
        self.last_symbol_values = None
        self.last_landmarks = None
        self.vertical_lines = []
        self.text_items = []

        self.max_value = 0

        # TODO?
        # self.setDownsampling(ds=10)

        # TODO: Gut, aber noch besser waere es wenn es der User auswaehlen koennte
        # self.enableAutoRange(axis='y')
        self.setMouseEnabled(x=True, y=False)

        self.legend = pg.LegendItem()
        self.legend.setParentItem(self.getPlotItem())

    def add_datalines(self, receiver_info):
        # self.legend.setColumnCount(len(receiver_info))
        for i in range(len(receiver_info)):
            description, sensor_descriptions = receiver_info[i]['description'], receiver_info[i]['sensor_descriptions']
            data_lines_ = []
            for j in range(len(sensor_descriptions)):
                data_line = self.plot([], [], name=description + ": " + sensor_descriptions[j], pen=self.plot_view.settings['pens'][i][j])
                data_lines_.append(data_line)
                self.legend.addItem(data_line, data_line.name())
            self.data_lines.append(data_lines_)

    def update_pens(self, receiver_index, sensor_index):
        pen = self.plot_view.settings['pens'][receiver_index][sensor_index]
        self.data_lines[receiver_index][sensor_index].setPen(pen)

    def remove_datalines(self):
        for i in range(len(self.data_lines)):
            for j in range(len(self.data_lines[i])):
                self.legend.removeItem(self.data_lines[i][j])
                self.data_lines[i][j].clear()
        self.data_lines = []
        self.last_vals = None
        for i in range(len(self.landmarks)):
            self.legend.removeItem(self.landmarks[i])
            self.landmarks[i].clear()
        self.landmarks = []
        self.last_landmarks = None
        self.deactivate_symbol_intervals()
        self.last_symbol_intervals = None
        self.deactivate_symbol_values()
        self.last_symbol_values = None
        self.max_value = 0
        self.update_()

    def update_values(self, vals):
        timestamps, values = vals['timestamps'], vals['values']
        for receiver_index in range(len(values)):
            if timestamps[receiver_index] is not None:
                for sensor_index in range(values[receiver_index].shape[1]):
                    if self.plot_view.settings['active'][receiver_index][sensor_index]:
                        # TODO: Only plot every x-th value, if it is too laggy
                        # self.data_lines[receiver_index][sensor_index].setData(timestamps[receiver_index][::1], values[receiver_index][:, sensor_index][::1])
                        x = timestamps[receiver_index]
                        y = values[receiver_index][:, sensor_index]
                        x = x[:len(y)]
                        y = y[:len(x)]
                        self.data_lines[receiver_index][sensor_index].setData(x, y)

        # TODO: ?
        try:
            self.max_value = max([np.max(a) for a in values])
        except:
            pass
        self.last_vals = vals

    def add_landmarks(self, landmark_info):
        num_landmarks = landmark_info['num']
        for i in range(num_landmarks):
            landmark_ = self.plot([], [], pen=None, symbol=self.plot_view.settings['landmarks_symbols'][i], name=landmark_info['names'][i])
            self.landmarks.append(landmark_)
            self.legend.addItem(landmark_, landmark_.name())

    def update_landmarks(self, landmarks):
        for i in range(len(landmarks)):
            if landmarks[i] is not None and self.plot_view.settings['landmarks_active'][i]:
                x, y = landmarks[i]['x'], landmarks[i]['y']
                self.landmarks[i].setData(x, y)
        self.last_landmarks = landmarks

    def activate_landmarks(self, landmark_index):
        if self.last_landmarks is not None and self.last_landmarks[landmark_index] is not None:
            x, y = self.last_landmarks[landmark_index]['x'], self.last_landmarks[landmark_index]['y']
            self.landmarks[landmark_index].setData(x, y)
            self.legend.addItem(self.landmarks[landmark_index], self.landmarks[landmark_index].name())

    def deactivate_landmarks(self, landmark_index):
        self.landmarks[landmark_index].clear()
        self.legend.removeItem(self.landmarks[landmark_index])
        self.update_()

    def update_landmarks_symbols(self, landmark_index):
        symbol = self.plot_view.settings['landmarks_symbols'][landmark_index]
        self.landmarks[landmark_index].setSymbol(symbol)

    def update_symbol_intervals(self, symbol_intervals):
        if self.plot_view.settings['symbol_intervals']:
            for timestamp in symbol_intervals[len(self.vertical_lines):]:
                vertical = pg.InfiniteLine(pos=timestamp, angle=90, movable=False, pen=self.plot_view.settings['symbol_intervals_pen'])
                self.addItem(vertical)
                self.vertical_lines.append(vertical)

        self.last_symbol_intervals = symbol_intervals

    def deactivate_symbol_intervals(self):
        for i in self.vertical_lines:
            self.removeItem(i)
        self.vertical_lines = []

    def activate_symbol_intervals(self):
        if self.last_symbol_intervals is not None:
            self.update_symbol_intervals(self.last_symbol_intervals)

    def update_symbol_values(self, symbol_intervals, symbol_values):
        # TODO: Why is this needed still?
        symbol_values = symbol_values[:len(symbol_intervals) - 1]

        if self.plot_view.settings['symbol_values']:
            for i in range(len(self.text_items), len(symbol_values)):
                # TODO: Special case for last value?
                # x_pos = symbol_intervals[i]
                x_pos = 0.5 * (symbol_intervals[i] + symbol_intervals[i+1])
                text = pg.TextItem(str(symbol_values[i]), color='k')
                # TODO: Place in correct height
                text.setPos(x_pos, 1.1 * self.max_value)
                self.addItem(text)
                self.text_items.append(text)
        self.last_symbol_values = symbol_values

    def deactivate_symbol_values(self):
        for text_item in self.text_items:
            self.removeItem(text_item)
        self.text_items = []

    def activate_symbol_values(self):
        if self.last_symbol_values:
            self.update_symbol_values(self.last_symbol_intervals, self.last_symbol_values)

    def deactivate_dataline(self, receiver_index, sensor_index):
        self.data_lines[receiver_index][sensor_index].clear()
        self.legend.removeItem(self.data_lines[receiver_index][sensor_index])
        self.update_()

    def update_(self):
        # Other way possible? update, repaint, resize, QApplication.processEvents do not work...
        self.hide()
        self.show()

    def activate_dataline(self, receiver_index, sensor_index):
        if self.last_vals is not None:
            timestamps, values = self.last_vals['timestamps'], self.last_vals['values']
            self.data_lines[receiver_index][sensor_index].setData(timestamps[receiver_index], values[receiver_index][:, sensor_index])
        self.legend.addItem(self.data_lines[receiver_index][sensor_index], self.data_lines[receiver_index][sensor_index].name())


class TimeAxisItem(pg.AxisItem):
    """
    Converts the timestamps from a float to a human-readable format for the x-axis ticks.
    """
    def tickStrings(self, values, scale, spacing):
        try:
            x = [datetime.fromtimestamp(value) for value in values]
            # x = [datetime.time(value) for value in values]
        # This catches the case that negative values can not be converted into timestamps
        except OSError:
            x = ['undefined'] * len(values)
        return x