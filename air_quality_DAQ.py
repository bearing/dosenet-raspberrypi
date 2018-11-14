import csv
import time
import numpy as np
from collections import deque
import serial
import sys
import os
from pyqtgraph.Qt import QtGui, QtCore
import pyqtgraph as pg

sys.stdout.flush()

class air_quality_DAQ(QtCore.QThread):
    def __init__ (self, n_merge):
        # self.sensor = sensor [Not sure if this is necessary]
        self.port = serial.Serial("/dev/serial0", baudrate=9600, timeout=1.5)
        self.data_signal = pg.QtCore.Signal(object)

        self.running = False
        self.n_merge = int(n_merge)
        self.PM01_list = []
        self.PM25_list = []
        self.PM10_list = []
        self.P3_list = []
        self.P5_list = []
        self.P10_list = []
        self.P25_list = []
        self.P50_list = []
        self.P100_list = []
        self.port = None
        self.aq_file = None
        self.results = None
        self.send_data = False

    def close(self,plot_id):
        plt.close(plot_id)

    def create_file(self, fname = None):
        file_time = time.strftime("%Y-%m-%d_%H-%M-%S", time.gmtime())
        id_info = []
        with open ('/home/pi/config/server_config.csv') as f:
            reader = csv.reader(f)
            for row in reader:
                id_info.append(row)
        if fname is None:
            filename =  "/home/pi/data/"+\
                        "_".join(row)+"_air_quality"+file_time+".csv"
        else:
            filename = fname
        self.aq_file = open(filename, "ab+")
        self.results = csv.writer(aq_file, delimiter = ",")
        metadata = ["Time", "0.3 um", "0.5 um", "1.0 um",
                    "2.5 um", "5.0 um", "10 um",
                    "PM 1.0", "PM 2.5", "PM 10"]
        self.results.writerow(metadata)

    def run(self):
        text = self.port.read(32)
        buffer = [ord(c) for c in text]
        if buffer[0] == 66:
            buf = buffer[1:32]

            # Get concentrations ug/m3
            PM01Val=repr((buf[3]<<8) + buf[4])
            PM25Val=repr((buf[5]<<8) + buf[6])
            PM10Val=repr((buf[7]<<8) + buf[8])

            # Get number of particles in 0.1 L of air above specific diameters
            P3  =repr((buf[15]<<8) + buf[16])
            P5  =repr((buf[17]<<8) + buf[18])
            P10 =repr((buf[19]<<8) + buf[20])
            P25 =repr((buf[21]<<8) + buf[22])
            P50 =repr((buf[23]<<8) + buf[24])
            P100=repr((buf[25]<<8) + buf[26])

            self.print_data(PM01Val,PM25Val,PM10Val,P3,P5,P10,P25,P50,P100)

            self.PM01_list.append(int(PM01Val))
            self.PM25_list.append(int(PM25Val))
            self.PM10_list.append(int(PM10Val))
            self.P3_list.append(int(P3))
            self.P5_list.append(int(P5))
            self.P10_list.append(int(P10))
            self.P25_list.append(int(P25))
            self.P50_list.append(int(P50))
            self.P100_list.append(int(P100))

            if len(PM25_list)>=n_merge:
                data = [time.time(),
                        np.mean(np.asarray(P3_list)),
                        np.mean(np.asarray(P5_list)),
                        np.mean(np.asarray(P10_list)),
                        np.mean(np.asarray(P25_list)),
                        np.mean(np.asarray(P50_list)),
                        np.mean(np.asarray(P100_list)),
                        np.mean(np.asarray(PM01_list)),
                        np.mean(np.asarray(PM25_list)),
                        np.mean(np.asarray(PM10_list))]
                self.results.writerow(data)

                data1 = [np.mean(np.asarray(PM01_list)),
                         np.std(np.asarray(PM01_list))]
                data2 = [np.mean(np.asarray(PM25_list)),
                         np.std(np.asarray(PM25_list))]
                data3 = [np.mean(np.asarray(PM10_list)),
                         np.std(np.asarray(PM10_list))]

            self.data_signal.emit([data1,data2,data3])
            self.clear_data()

    def close_file(self):
        sys_cmd = 'scp {} pi@192.168.4.1:/home/pi/data'.format(
                                                        self.aq_file.name)
        print(sys_cmd)
        os.system(sys_cmd)

        self.aq_file.close()

    def clear_data(self):
        self.P3_list[:] = []
        self.P5_list[:] = []
        self.P10_list[:] = []
        self.P25_list[:] = []
        self.P50_list[:] = []
        self.P100_list[:] = []
        self.PM01_list[:] = []
        self.PM25_list[:] = []
        self.PM10_list[:] = []

    def print_data(self,PM01Val,PM25Val,PM10Val,P3,P5,P10,P25,P50,P100):
        print('Concentration of Particulate Matter [ug/m3]')
        print('PM 1.0 = {} ug/m3'.format(PM01Val))
        print('PM 2.5 = {} ug/m3'.format(PM25Val))
        print('PM 10  = {} ug/m3\n'.format(PM25Val))

        # Print number of particles in 0.1 L of air over specific diamaters
        '''
        print('Number of particles in 0.1 L of air with specific diameter\n')
        print('#Particles, diameter over 0.3 um = {}'.format(P3))
        print('#Particles, diameter over 0.5 um = {}'.format(P5))
        print('#Particles, diameter over 1.0 um = {}'.format(P10))
        print('#Particles, diameter over 2.5 um = {}'.format(P25))
        print('#Particles, diameter over 5.0 um = {}'.format(P50))
        print('#Particles, diameter over 10  um = {}'.format(P100))
		'''
