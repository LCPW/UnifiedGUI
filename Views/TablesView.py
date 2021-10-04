from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *


from Views import TableView


class TablesView(QWidget):
    def __init__(self):
        super().__init__()

        layout = QVBoxLayout()

        self.tabs = QTabWidget()
        self.tables = []
        #self.tab_table1 = TableView.TableView()
        #self.tab_table2 = TableView.TableView()

        #self.tabs.addTab(self.tab_table1, "Table1")
        #self.tabs.addTab(self.tab_table2, "Table2")

        layout.addWidget(self.tabs)

        self.setLayout(layout)

    def add_tables(self, count):
        for i in range(count):
            self.tables.append(TableView.TableView())
            self.tabs.addTab(self.tables[i], str(i))

    def update_values(self, vals):
        for i in range(len(vals)):
            self.tables[i].update_values(vals[i])
        #self.tab_table1.update_values(vals[0])
        #self.tab_table2.update_values(vals[1])