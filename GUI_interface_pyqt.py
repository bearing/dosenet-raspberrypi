import sys
import numpy as np
import math
import datetime as dt
import time
import D3S_pyqt_DAQ as D3S
import air_quality_DAQ as AQ

from PyQt5.QtWidgets import QApplication, QWidget, QMainWindow, QPushButton
from PyQt5.QtWidgets import QAction, QLineEdit, QMessageBox, QLabel
from PyQt5.QtWidgets import QMenu, QGridLayout, QFormLayout
from PyQt5.QtWidgets import QCheckBox
from pyqtgraph import QtCore, QtGui
from PyQt5.QtCore import pyqtSlot, Qt
from PyQt5.QtGui import QPalette, QFont, QTabWidget, QTabBar, QComboBox
from PyQt5.QtGui import QStyleFactory

import pyqtgraph as pg

import random

# Various function calls to set general look
pg.setConfigOptions(antialias=True)
pg.setConfigOption('background', 'w')
pg.setConfigOption('foreground', 'k')

# Set text for sensor types
RAD = "Radiation"
AIR = "Air Quality"
CO2 = "CO2"
PTH = "P/T/H"

class App(QWidget):

    def __init__(self, nbins=4096):
        super().__init__()
        self.title = 'PyQt5 simple window'
        self.left = 0
        self.top = 0
        self.width = 1280
        self.height = 720
        self.nbins = nbins
        self.ndata = 25
        self.start_time = None
        self.plot_list = {}
        self.err_list = {}
        self.sensor_list = {}
        self.data_display = {}
        self.data = {}
        self.time_data = {}
        self.saveData = True
        self.channels = np.arange(self.nbins, dtype=int)
        self.initUI()

    def initUI(self):
        self.setAutoFillBackground(True)
        self.setBackgroundRole(QPalette.Base)
        self.initLayout()
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)
        self.setLayout(self.layout)

    def initLayout(self):
        # Create Grid layout
        self.layout = QGridLayout()
        #self.layout.setSpacing(0.)
        self.layout.setContentsMargins(0.,0.,0.,0.)

        # Create main plotting area
        self.tabs = QTabWidget(self)
        self.tabs.setStyleSheet("QTabWidget::tab-bar { alignment: left; } "+\
                "QTabWidget::pane { border: 2px solid #404040; } "+\
                "QTabBar {font-size: 18pt;}");
        tab_bar = QTabBar()
        tab_bar.setStyleSheet("QTabBar::tab { height: 80px; width: 150px;}")
        self.tabs.setTabBar(tab_bar)
        ptop, pleft, pheight, pwidth = 0, 0, 12, 9
        self.layout.addWidget(self.tabs,ptop,pleft,pheight,pwidth)
        self.setSelectionTab()

        # Create text label
        label = QLabel('Select sensors', self)
        textfont = QFont("Times", 20, QFont.Bold)
        label.setFont(textfont)
        self.layout.addWidget(label,ptop,pleft+pwidth+1,1,1)
        label.setAlignment(Qt.AlignCenter)

        # Create checkboxes for each sensor
        self.addCheckBox(RAD,ptop+1,pleft+pwidth+1)
        self.addCheckBox(AIR,ptop+2,pleft+pwidth+1)
        self.addCheckBox(CO2,ptop+3,pleft+pwidth+1)
        self.addCheckBox(PTH,ptop+4,pleft+pwidth+1)

        # Create textbox
        #self.textbox = QLineEdit(self)
        #self.layout.addWidget(self.textbox,ptop+1,pleft+pwidth+1,1,1)
        #self.textbox.setAlignment(Qt.AlignCenter)

        # Create push button
        #self.addButton('Update Plot',self.on_click,ptop+2,pleft+pwidth+1,1,1)
        self.addButton('Start',self.run,ptop+8,pleft+pwidth+1,1,1,"#66B2FF")
        self.addButton('Stop',self.stop,ptop+9,pleft+pwidth+1,1,1,"#FF6666")
        self.addButton('Clear',self.clear,ptop+10,pleft+pwidth+1,1,1,"#E0E0E0")


    def addButton(self,label,method,top,left,height,width,color="white"):
        button = QPushButton(label, self)
        style_sheet_text = "background-color: "+color+";"+\
                           "border-style: outset;"+\
                           "border-width: 3px;"+\
                           "border-radius: 2px;"+\
                           "border-color: beige;"+\
                           "font: bold 14px;"+\
                           "min-width: 10em;"+\
                           "padding: 6px;"

        button.setStyleSheet(style_sheet_text)
        button.clicked.connect(method)
        self.layout.addWidget(button,top,left,height,width,Qt.AlignHCenter)


    def addCheckBox(self, label, top, left):
        checkbox = QCheckBox(label)
        textfont = QFont("Times", 18, QFont.Bold)
        checkbox.setFont(textfont)
        checkbox.setChecked(False)
        checkbox.stateChanged.connect(lambda:self.sensorButtonState(checkbox))
        self.layout.addWidget(checkbox,top,left,1,1,Qt.AlignHCenter)


    def sensorButtonState(self,b):
     if b.isChecked() == True:
        print("{} is selected".format(b.text()))
        self.addSensor(b.text())
     else:
        #TODO add method to delete sensor from sensor list dict
        print("{} is deselected".format(b.text()))


    def set_display_text(self, sensor):
        full_text = ' '.join(str(r) for r in self.sensor_list[sensor])
        self.data_display[sensor].setText(full_text)


    def setSelectionTab(self):
        self.selection_tab = QWidget()
        self.tabs.addTab(self.selection_tab, "Configure")
        self.config_layout = QFormLayout()
        self.config_layout.setContentsMargins(30.,50.,30.,20.)
        integration_text = QLabel("Integration time (sec):")
        textfont = QFont("Times", 22, QFont.Bold)
        integration_text.setFont(textfont)
        integration_text.setAlignment(Qt.AlignCenter)
        integration_box = QComboBox()
        item_list = ["1","2","3","4","5","10","15","20","30","60"]
        integration_box.addItems(item_list)
        integration_box.setCurrentIndex(1)
        integration_box.currentIndexChanged.connect(
            lambda:self.setIntegrationTime(str(integration_box.currentText())))
        self.config_layout.addRow(integration_text,integration_box)

        ndata_text = QLabel("# of Data Points to display:")
        ndata_text.setFont(textfont)
        ndata_text.setAlignment(Qt.AlignCenter)
        ndata_box = QComboBox()
        item_list = ["5","10","15","20","25","30","40","50","60"]
        ndata_box.addItems(item_list)
        ndata_box.setCurrentIndex(4)
        ndata_box.currentIndexChanged.connect(
                lambda:self.setNData(str(ndata_box.currentText())))
        self.config_layout.addRow(ndata_text,ndata_box)

        checkbox = QCheckBox("Save Data")
        checkbox.setFont(textfont)
        checkbox.setChecked(True)
        checkbox.stateChanged.connect(lambda:self.setSaveData(checkbox))
        self.config_layout.addWidget(checkbox)

        self.group_text = QLabel("Group Number:")
        textfont = QFont("Times", 22, QFont.Bold)
        self.group_text.setFont(textfont)
        self.group_text.setAlignment(Qt.AlignCenter)
        self.group_box = QComboBox()
        item_list = ["1","2","3","4","5","6","7","8","9","10"]
        self.group_id = "1"
        self.group_box.addItems(item_list)
        self.group_box.currentIndexChanged.connect(
                lambda:self.setGroupID(str(self.group_box.currentText())))
        self.config_layout.addRow(self.group_text,self.group_box)

        self.ptext = QLabel("Period:")
        self.ptext.setFont(textfont)
        self.ptext.setAlignment(Qt.AlignCenter)
        self.pbox = QComboBox()
        item_list = ["1","2","3","4","5","6","7","8"]
        self.period_id = "1"
        self.pbox.addItems(item_list)
        self.pbox.currentIndexChanged.connect(
                lambda:self.setPeriodID(str(self.pbox.currentText())))
        self.config_layout.addRow(self.ptext,self.pbox)

        self.location_text = QLabel("Location:")
        self.location_text.setFont(textfont)
        self.location_text.setAlignment(Qt.AlignCenter)
        self.location_box = QComboBox()
        item_list = ["Inside","Outside","Test_1","Test_2","Test_3"]
        self.location = "Inside"
        self.location_box.addItems(item_list)
        self.location_box.currentIndexChanged.connect(
                lambda:self.setLocation(str(self.location_box.currentText())))
        self.config_layout.addRow(self.location_text,self.location_box)

        self.selection_tab.setLayout(self.config_layout)


    def setSaveData(self,b):
        if b.isChecked() == True:
            print("Saving sensor data")
            self.saveData = True
            self.group_text.show()
            self.group_box.show()
            self.ptext.show()
            self.pbox.show()
            self.location_text.show()
            self.location_box.show()
        else:
            self.saveData = False
            self.group_text.close()
            self.group_box.close()
            self.ptext.close()
            self.pbox.close()
            self.location_text.close()
            self.location_box.close()

    def setIntegrationTime(self,):
        self.integration_time = int(text)

    def setNData(self,text):
        self.ndata = int(text)

    def setGroupID(self,text):
        self.group_id = text

    def setPeriodID(self,text):
        self.period_id = text

    def setLocation(self,text):
        self.location = text

    def addSensor(self, sensor):
        self.initSensorData(sensor)
        self.setSensorTab(sensor)
        self.setSensorText(sensor)


    def setSensorTab(self, sensor):
        # Create canvas for plots
        itab = QWidget()
        self.tabs.addTab(itab, sensor)
        tablayout = QGridLayout()
        tablayout.setSpacing(0.)
        tablayout.setContentsMargins(0.,0.,0.,0.)

        # Create value display
        self.data_display[sensor] = QLabel("")
        textfont = QFont("Times", 20, QFont.Bold)
        self.data_display[sensor].setFont(textfont)
        self.data_display[sensor].setStyleSheet("background-color:#33FF99;")
        self.data_display[sensor].setAlignment(Qt.AlignCenter)
        tablayout.addWidget(self.data_display[sensor],0,2,1,4)
        tablayout.setRowStretch(0,2)

        self.setPlots(sensor,tablayout)
        itab.setLayout(tablayout)


    def setPlots(self,sensor,layout):
        if sensor==RAD:
            splotwin = pg.GraphicsWindow()
            splotwin.setContentsMargins(0,0,0,0)
            splot = splotwin.addPlot(title="<h2> {} Data </h2>".format(sensor))
            splot.showGrid(x=True, y=True)
            splot.setLabel('left', '<h3>Counts/Channel</h3>')
            splot.setLabel('bottom', '<h3>Channel</h3>')
            curve1 = splot.plot(self.channels, self.data[sensor],
                                symbolBrush=(255,0,0), symbolPen='k',
                                pen=(255, 0, 0))

            tplotwin = pg.GraphicsWindow()
            tplotwin.setContentsMargins(0,0,0,0)
            tplot = tplotwin.addPlot()
            tplot.showGrid(x=True, y=True)
            tplot.setLabel('left', '<h3>CPM</h3>')
            tplot.setLabel('bottom', '<h3>Time</h3>')
            err = pg.ErrorBarItem()
            tplot.addItem(err)
            curve2 = tplot.plot(symbolBrush=(255,0,0), symbolPen='k',
                                pen=(255, 0, 0))
            self.plot_list[sensor] = [curve1,curve2]
            self.err_list[sensor] = err
            layout.addWidget(splotwin,1,0,1,8)
            layout.setRowStretch(1,15)
            layout.addWidget(tplotwin,2,0,1,8)
            layout.setRowStretch(2,5)

        if sensor==AIR:
            plotwin = pg.GraphicsWindow()
            plotwin.setContentsMargins(0,0,0,0)
            iplot = plotwin.addPlot(title="<h1> {} Data </h1>".format(sensor))
            iplot.showGrid(x=True, y=True)
            legend = pg.LegendItem(size=(110,90), offset=(100,10))
            legend.setParentItem(iplot)
            #iplot.addLegend()
            iplot.setLabel('left', '<h2>Particulate Concentration</h2>')
            iplot.setLabel('bottom', '<h2>Time</h2>')
            colors = [(255,0,0),(0,255,0),(0,0,255)]
            names = ['<h4>PM 1.0</h4>',
                     '<h4>PM 2.5</h4>',
                     '<h4>PM 10</h4>']

            self.plot_list[sensor] = []
            for idx in range(len(self.data[sensor])):
                err = pg.ErrorBarItem()
                iplot.addItem(err)
                curve = iplot.plot(self.time_data[sensor],
                                   self.data[sensor][idx],
                                   symbolBrush=colors[idx], symbolPen='k',
                                   pen=colors[idx], name=names[idx])
                self.err_list[sensor].append(err)
                self.plot_list[sensor].append(curve)
                legend.addItem(curve,names[idx])
            layout.addWidget(plotwin,1,0,1,8)
            layout.setRowStretch(1,20)


    def setSensorText(self, sensor):
        if sensor==RAD:
            cpm = "{:.1f}".format(np.mean(self.data[sensor]))
            usv = "{:.3f}".format(np.mean(self.data[sensor]) * 0.005)
            sensor_text = ["CPM =",cpm,"                  uSv/hr =",usv]
            self.sensor_list[sensor] = sensor_text

        if sensor==AIR:
            if len(self.data[sensor][0]) == 0:
                pm1, pm25, pm10 = 0., 0., 0.
            else:
                pm1 = "{:.1f}".format(np.mean(self.data[sensor][0]))
                pm25 = "{:.1f}".format(np.mean(self.data[sensor][1]))
                pm10 = "{:.1f}".format(np.mean(self.data[sensor][2]))
            sensor_text = ["PM 1.0 =",pm1,
                           "ug/L     PM 2.5 =",pm25,
                           "ug/L     PM 10 =",pm10,"ug/L"]
            self.sensor_list[sensor] = sensor_text
        self.set_display_text(sensor)


    def initSensorData(self,sensor):
        self.time_data[sensor] = []
        if sensor==RAD:
            self.d3s_daq = D3S.DAQThread()
            self.d3s_daq.spectrum_signal.connect(updateD3S)
            self.data[sensor] = np.zeros(self.nbins, dtype=float)
            self.ave_data = [[],[]]

        if sensor==AIR:
            self.aq_daq = AQ.air_quality_DAQ(self.interval*5)
            self.aq_daq.data_signal.connect(updateAirData)
            if self.saveData:
                fname = "/home/pi/data/AQ_G" + self.group_id + "_P" + \
                        self.period_id + "_" + self.location + "_" + \
                        str(datetime.datetime.today()).split()[0]+".csv"
                self.aq_daq.create_file(fname)
            self.data[sensor] = [[[],[]],[[],[]],[[],[]]]


    def updateD3S(self, data):
        self.d3s_data += data
        updatePlot(RAD)


    def updateAirData(self, data):
        data1, err1 = data[0][0], data[0][1]
        data2, err2 = data[1][0], data[1][1]
        data3, err3 = data[2][0], data[2][1]
        self.data[AIR][0][0].append(data1)
        self.data[AIR][0][1].append(err1)
        self.data[AIR][1][0].append(data2)
        self.data[AIR][1][1].append(err2)
        self.data[AIR][2][0].append(data3)
        self.data[AIR][2][1].append(err3)
        updatePlot(AIR)


    def updatePlot(self, sensor):
        # Make sure start_time is defined
        #  - if it's not restart the time count now
        if self.start_time is None:
            self.start_time = float(format(float(time.time()), '.2f'))
        itime = float(format(float(time.time()), '.2f')) - self.start_time
        self.time_data[sensor].append(itime)
        if len(self.time_data[sensor]) > self.ndata:
            self.time_data[sensor].pop(0)

        if sensor==RAD:
            self.data[sensor] += self.d3s_data
            self.plot_list[sensor][0].setData(self.channels, self.data[sensor])
            cpm = np.mean(self.data[sensor])
            err = np.std(self.data[sensor])
            self.ave_data[0].append(cpm)
            self.ave_data[1].append(err)
            if len(self.ave_data) > self.ndata:
                self.ave_data[0].pop(0)
                self.ave_data[1].pop(0)
            self.err_list[sensor].setData(x=self.time_data[sensor],
                                          y=self.ave_data[0],
                                          height=self.ave_data[1],
                                          beam=0.2)
            self.plot_list[sensor][1].setData(self.time_data[sensor],
                                              self.ave_data[0])

        if sensor==AIR:
            if len(self.data[sensor][0][0]) > self.ndata:
                self.data[sensor][0][0].pop(0)
                self.data[sensor][0][1].pop(0)
                self.data[sensor][1][0].pop(0)
                self.data[sensor][1][1].pop(0)
                self.data[sensor][2][0].pop(0)
                self.data[sensor][2][1].pop(0)

            self.err_list[sensor][0].setData(x=self.time_data[sensor],
                                             y=self.data[sensor][0][0],
                                             height=self.data[sensor][0][1],
                                             beam=0.2)
            self.plot_list[sensor][0].setData(self.time_data[sensor],
                                              self.data[sensor][0][0])
            self.err_list[sensor][1].setData(x=self.time_data[sensor],
                                             y=self.data[sensor][1][0],
                                             height=self.data[sensor][1][1],
                                             beam=0.2)
            self.plot_list[sensor][1].setData(self.time_data[sensor],
                                              self.data[sensor][1][0])
            self.err_list[sensor][2].setData(x=self.time_data[sensor],
                                             y=self.data[sensor][2][0],
                                             height=self.data[sensor][2][1],
                                             beam=0.2)
            self.plot_list[sensor][2].setData(self.time_data[sensor],
                                              self.data[sensor][2][0])
        self.updateText(sensor)


    def updateText(self, sensor):
        if sensor==RAD:
            cpm = "{:.1f}".format(np.mean(self.data[sensor]))
            usv = "{:.3f}".format(np.mean(self.data[sensor]) * 0.005)
            self.sensor_list[sensor][1] = cpm
            self.sensor_list[sensor][3] = usv

        if sensor==AIR:
            pm1 = "{:.1f}".format(np.mean(self.data[sensor][0][0]))
            pm25 = "{:.1f}".format(np.mean(self.data[sensor][1][0]))
            pm10 = "{:.1f}".format(np.mean(self.data[sensor][2][0]))
            self.sensor_list[sensor][1] = pm1
            self.sensor_list[sensor][3] = pm25
            self.sensor_list[sensor][5] = pm10

        self.set_display_text(sensor);


    @pyqtSlot()
    def updatePlots(self):
        for sensor in self.sensor_list:
            self.updatePlot(sensor)

    @pyqtSlot()
    def run(self):
        print("Starting data collection")
        # Only set start time the first time user clicks start
        if self.start_time is None:
            self.start_time = float(format(float(time.time()), '.2f'))
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.updatePlots)
        self.timer.start(500)

    @pyqtSlot()
    def stop(self):
        self.timer.stop()

    @pyqtSlot()
    def clear(self):
        # Reset start time to None to reset time axis
        self.start_time = None
        for sensor in self.sensor_list:
            self.time_data[sensor] = []
            if sensor==RAD:
                self.data[sensor] = np.zeros(self.nbins, dtype=float)
                self.ave_data = []
            if sensor==AIR:
                self.data[sensor] = [[],[],[]]


if __name__ == '__main__':
    # Enable antialiasing for prettier plots
    app = QApplication(sys.argv)
    QApplication.setStyle(QStyleFactory.create("Cleanlooks"))
    nbins = 4096
    ex = App(nbins=nbins)
    ex.show()

    #ex.update_plot(data)
    #app.processEvents()
    sys.exit(app.exec_())
