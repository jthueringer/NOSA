from PyQt5 import QtCore, QtWidgets, QtGui
import quantities as pq
import numpy as np

class ABFLoaderDialog(QtWidgets.QDialog):

    def __init__(self, parent, abf):

        QtWidgets.QDialog.__init__(self, parent, flags = QtCore.Qt.WindowTitleHint | QtCore.Qt.WindowCloseButtonHint)

        self.setWindowTitle('ABF Import Settings')
        self.setModal(True)

        layout = QtWidgets.QVBoxLayout()
        self.setLayout(layout)

        layout.addWidget(QtWidgets.QLabel('Please choose the data you want to import.'))

        self.connect_checkbox = QtWidgets.QCheckBox('Connect continuous sweeps that belong to the same recording channel')
        layout.addWidget(self.connect_checkbox)
        self.connect_checkbox.setChecked(False)
        self.connect_checkbox.stateChanged.connect(self.checkboxStateChanged)

        self.table = QtWidgets.QTableWidget()
        layout.addWidget(self.table)
        self.table.setColumnCount(8)
        self.table.setHorizontalHeaderLabels(['', 'Name', 'Mean', 'Begin', 'End', 'Unit', 'Length (frames)', 'Description'])
        for i in range(7):
            self.table.horizontalHeader().setResizeMode(i, QtGui.QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setFixedHeight(QtGui.QFontMetrics(self.table.horizontalHeader().font()).height() + 10)
        self.table.verticalHeader().setVisible(False)
        self.table.verticalHeader().setDefaultSectionSize(20)
        self.table.setStyleSheet('QCheckBox{background-color:rgba(1,1,1,0);}')
        self.table.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.table.setRowCount(0)

        self.connected_data = []
        self.unconnected_data = []
        unconnected_counter = 0

        for channel_index in abf.channelList:
            connected_data = np.array([], dtype = np.float32)
            for sweep in abf.sweepList:
                abf.setSweep(sweepNumber = sweep, channel = channel_index)
                unconnected_counter += 1
                self.unconnected_data.append(
                    {
                        'tabledata':
                        [
                            unconnected_counter,
                            '{} (sweep {})'.format(abf.adcNames[channel_index], str(sweep)),
                            np.mean(abf.sweepY),
                            abf.sweepY[0],
                            abf.sweepY[-1],
                            abf.adcUnits[channel_index],
                            abf.sweepPointCount,
                            None
                        ],
                        'data': abf.sweepY
                    }
                )
                connected_data = np.concatenate((connected_data, abf.sweepY))
            
            self.connected_data.append(
                {
                    'tabledata':
                    [
                        channel_index+1,
                        abf.adcNames[channel_index],
                        np.mean(connected_data),
                        connected_data[0],
                        connected_data[-1],
                        abf.adcUnits[channel_index],
                        len(connected_data),
                        None
                    ],
                    'data': connected_data
                }
            )
        button_widget = QtWidgets.QWidget()
        layout.addWidget(button_widget)

        button_layout = QtWidgets.QHBoxLayout()
        button_widget.setLayout(button_layout)
        
        ok_button = QtWidgets.QPushButton('Ok')
        button_layout.addWidget(ok_button)
        ok_button.clicked.connect(self.accept)

        cancel_button = QtWidgets.QPushButton('Cancel')
        button_layout.addWidget(cancel_button)
        cancel_button.clicked.connect(self.reject)

        self.showTable(connected = False)

        self.setMinimumWidth(self.table.width())
        
    def checkboxStateChanged(self, state):
        if state == QtCore.Qt.Checked:
            self.showTable(connected = True)
        else:
            self.showTable(connected = False)

    def showTable(self, connected):
        self.table.setRowCount(0)
        self.checkboxes = []

        for row, data in enumerate(self.connected_data if connected else self.unconnected_data):
            self.table.insertRow(row)
            checkbox = QtWidgets.QCheckBox(str(data['tabledata'][0]))
            self.checkboxes.append(checkbox)
            self.table.setCellWidget(row, 0, checkbox)
            for i in range(1, len(data['tabledata'])):
                self.table.setItem(row, i, QtWidgets.QTableWidgetItem(str(data['tabledata'][i])))

    def getSelectedData(self):
        selected_data = []
        data_array = self.connected_data if self.connect_checkbox.isChecked() else self.unconnected_data
        displayed_options = len(data_array)
        for checkbox, data in zip(self.checkboxes, data_array):
            if checkbox.isChecked():
                selected_data.append(data)
        return selected_data, displayed_options