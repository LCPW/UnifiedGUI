from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
import pyqtgraph as pg
from datetime import datetime


# TODO: Make non-ugly
COLORS = [pg.mkColor("#0000ff"), pg.mkColor("#cc0029"), pg.mkColor("#00d5ff"), pg.mkColor("#b3ff00"),
          pg.mkColor("#ff8000"), pg.mkColor("#ff0000"), pg.mkColor("#000000")]


class PlotWidgetView(pg.PlotWidget):
    def __init__(self):
        super().__init__(axisItems={'bottom': TimeAxisItem(orientation='bottom')})

        # Set background color to white
        self.setBackground('w')

        # Axis labels left and bottom
        self.setLabel('left', "Value")
        self.setLabel('bottom', "Time")

        # Grid
        self.showGrid(x=True, y=True)

        self.receiver_data_lines = []

        self.addLegend()

        #self.legend = pg.LegendItem()
        #self.legend.setParentItem(self.getPlotItem())

    def update(self):
        #for receiver_data_lines in self.receiver_data_lines:
            #receiver_data_lines.update()
        pass

    def add_datalines(self, receiver_info):
        for i in range(len(receiver_info)):
            description, sensor_descriptions = receiver_info[i]['description'], receiver_info[i]['sensor_descriptions']
            data_line = ReceiverDataLines(self, description, sensor_descriptions)
            self.receiver_data_lines.append(data_line)

    def remove_datalines(self):
        # TODO: Empty all lists before deleting?
        self.receiver_data_lines = []

    def update_values(self, vals):
        if vals is None:
            return
        #print(vals)
        timestamps, values = vals['timestamps'], vals['values']
        for i in range(len(timestamps)):
            # self.receiver_data_lines[i].timestamps = timestamps[i]
            #print(values[i])
            # TODO: ?
            if values[i] is None:
                return

            for j in range(values[i].shape[1]):
                y = values[i][:, j]
                #print(timestamps[i])
                #print(y)
                self.receiver_data_lines[i].data_lines[j].setData(x=timestamps[i], y=y)
        #for i in range(len(vals)):
        #   self.receiver_data_lines[i].update_values(vals[i])

    def clear(self):
        for i in range(len(self.receiver_data_lines)):
            self.receiver_data_lines[i].clear()

    def get_color(self, index):
        return pg.intColor(index)


class ReceiverDataLines:
    def __init__(self, plot_widget, description, sensor_descriptions):
        self.plot_widget = plot_widget
        self.description = description
        self.sensor_descriptions = sensor_descriptions
        self.timestamps = []
        self.values = []
        self.data_lines = []

        for i in range(len(sensor_descriptions)):
            self.values.append([])
            # pg.intColor evtl. verwenden
            pen = pg.mkPen(width=2, color=COLORS.pop(0))
            self.data_lines.append(self.plot_widget.plot([], [], name=self.description + ": " + self.sensor_descriptions[i], pen=pen))

    def update_values(self, vals):
        for i in range(len(self.timestamps), len(vals)):
            timestamp, values = vals[i]['timestamp'], vals[i]['values']
            self.timestamps.append(timestamp)
            for j in range(len(values)):
                self.values[j].append(values[j])

    def clear(self):
        for i in range(len(self.data_lines)):
            self.data_lines[i].clear()


class TimeAxisItem(pg.AxisItem):
    def tickStrings(self, values, scale, spacing):
        x = [datetime.fromtimestamp(value) for value in values]
        return x