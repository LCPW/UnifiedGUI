from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
import pyqtgraph as pg
from datetime import datetime


class PlotView(pg.PlotWidget):
    def __init__(self):
        super().__init__(axisItems={'bottom': TimeAxisItem(orientation='bottom')})

        # Set background color to white
        self.setBackground('w')

        # Axis labels left and bottom
        self.setLabel('left', "y")
        self.setLabel('bottom', "x")

        # Grid
        self.showGrid(x=True, y=True)

        self.timestamps = []
        self.y = []
        self.data_line = self.plot([], [], name="1")

    def update_values(self, vals):
        self.timestamps = []
        self.y = []
        for t, x in vals:
            self.timestamps.append(t)
            #self.timestamps.append(len(self.timestamps))
            self.y.append(x)
        tx = [x.timestamp() for x in self.timestamps]
        # print(tx)
        self.data_line.setData(x=tx, y=self.y)


class TimeAxisItem(pg.AxisItem):
    def tickStrings(self, values, scale, spacing):
        x = [datetime.fromtimestamp(value) for value in values]
        return x