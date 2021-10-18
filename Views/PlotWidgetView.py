from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
import pyqtgraph as pg
from datetime import datetime
import numpy as np


class PlotWidgetView(pg.PlotWidget):
    def __init__(self, plot_view):
        super().__init__(axisItems={'bottom': TimeAxisItem(orientation='bottom')})

        self.plot_view = plot_view

        # Set background color to white
        self.setBackground('w')

        # Axis labels left and bottom
        self.setLabel('left', "Value")
        self.setLabel('bottom', "Time")

        # Grid
        self.showGrid(x=True, y=True)

        self.data_lines = []

        self.addLegend()

        # TODO
        # self.setDownsampling(ds=10)
        # self.setYRange(0, 1)
        # self.disableAutoRange()

        #self.legend = pg.LegendItem()
        #self.legend.setParentItem(self.getPlotItem())

    def add_datalines(self, receiver_info):
        for i in range(len(receiver_info)):
            description, sensor_descriptions = receiver_info[i]['description'], receiver_info[i]['sensor_descriptions']
            data_lines_ = []
            for j in range(len(sensor_descriptions)):
                # pen = pg.mkPen(width=2, color=self.plot_view.settings['colors'][i][j])
                data_lines_.append(self.plot([], [], name=description + ": " + sensor_descriptions[j], pen=self.plot_view.settings['pens'][i][j]))
            self.data_lines.append(data_lines_)

    def update_pens(self, i, j):
        pen = self.plot_view.settings['pens'][i][j]
        self.data_lines[i][j].setPen(pen)

    def remove_datalines(self):
        # TODO
        pass

    def update_values(self, vals):
        timestamps, values = vals['timestamps'], vals['values']
        for receiver_index in range(len(timestamps)):
            if timestamps[receiver_index] is not None:
                for sensor_index in range(values[receiver_index].shape[1]):
                    if self.plot_view.settings['active'][receiver_index][sensor_index]:
                        self.data_lines[receiver_index][sensor_index].setData(timestamps[receiver_index][::1], values[receiver_index][:, sensor_index][::1])
                        # self.setXRange(timestamps[receiver_index][0], timestamps[receiver_index][-1])
                    else:
                        self.data_lines[receiver_index][sensor_index].clear()

    # def clear_(self):
    #     for receiver_index in range(len(self.data_lines)):
    #         for sensor_index in range(len(self.data_lines[receiver_index])):
    #             self.data_lines[receiver_index][sensor_index].clear()
    #             self.plot_view.settings['active'][receiver_index][sensor_index] = False
    #
    # def clear2(self, i, j):
    #     self.data_lines[i][j].clear()


class TimeAxisItem(pg.AxisItem):
    """
    Converts the timestamps from a float to a human-readable format for the x-axis ticks.
    """
    def tickStrings(self, values, scale, spacing):
        x = [datetime.fromtimestamp(value) for value in values]
        return x


def get_color(index):
    return pg.intColor(index)