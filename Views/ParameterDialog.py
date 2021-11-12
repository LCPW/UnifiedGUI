from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *


class ParameterDialog(QDialog):
    def __init__(self, parameters):
        super(ParameterDialog, self).__init__()

        self.setWindowTitle("Parameters")
        self.setWindowIcon(QIcon('./Views/Icons/tune.png'))

        self.values = {}
        self.widgets = []

        layout = QFormLayout()
        for i in range(len(parameters)):
            param = parameters[i]
            description = param['description']
            label = QLabel(description)
            type_ = param['dtype']
            w = None
            # self.values[i] = param['default']
            if type_ == 'bool':
                w = QCheckBox()
                w.setChecked(param['default'])
                #w.clicked.connect(generate_lambda(i, w.isChecked()))
            elif type_ == 'int':
                w = QSpinBox()
                w.setRange(param['min'], param['max'])
                w.setValue(param['default'])
                #w.valueChanged.connect(generate_lambda(i, w.value()))
                # Evtl. noch singleStep
                # w.Value()
            elif type_ == 'float':
                w = QDoubleSpinBox()
                w.setRange(param['min'], param['max'])
                w.setValue(param['default'])
                w.setDecimals(param['decimals'])
                #w.valueChanged.connect(generate_lambda(i, w.value()))
                # Evtl. noch singleStep
            elif type_ == 'item':
                w = QComboBox()
                w.addItems(param['items'])
                # TODO: Check if default is actually in items
                w.setCurrentIndex(param['items'].index(param['default']))
                #w.activated.connect(generate_lambda(i, w.currentText()))
            elif type_ == 'string':
                w = QLineEdit()
                w.setMaxLength(param['max_length'])
                w.setText(param['default'])
                #w.textEdited.connect(generate_lambda(i, w.text()))
            self.widgets.append((w, type_, description))
            layout.addRow(label, w)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept_)
        buttons.rejected.connect(self.reject)
        layout.addRow(buttons)

        self.setLayout(layout)

    def accept_(self):
        for w, t, description in self.widgets:
            value = None
            if t == 'bool':
                value = w.isChecked()
            elif t == 'int' or t == 'float':
                value = w.value()
            elif t == 'item':
                value = w.currentText()
            elif t == 'string':
                value = w.text()
            self.values[description] = value
        #print(self.values)
        self.accept()