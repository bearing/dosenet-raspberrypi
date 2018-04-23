# July 18th, 2017 15:49
# Code by Jennifer Atkins
# Based off of code by Ludi Cao

import time
import datetime
import csv
import numpy as np
from matplotlib.dates import DateFormatter
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
from collections import deque
import serial
import sys
sys.stdout.flush()

#sensor = entercodehere(morestuff) [Not sure if this is necessary] 

class air_quality_DAQ(object):
    def __init__ (self, maxdata, n_merge):
        # self.sensor = sensor [Not sure if this is necessary]
        self.running = False
        self.time_queue = deque()
        self.PM01_queue = deque()
        self.PM25_queue = deque()
        self.PM10_queue = deque()
        self.PM01_error = deque()
        self.PM25_error = deque()
        self.PM10_error = deque()        
        self.P3_queue = deque()
        self.P5_queue = deque()
        self.P10_queue = deque()
        self.P25_queue = deque()
        self.P50_queue = deque()
        self.P100_queue = deque()
        self.maxdata = int(maxdata)
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
        self.time_list = []
        self.merge_test=False
        self.port = None
        self.first_data = True
        self.last_time = None
            
    def close(self,plot_id):
        plt.close(plot_id)

    def create_file(self):
        global results
        global f
        file_time = time.strftime("%Y-%m-%d_%H-%M-%S", time.gmtime())
        id_info = []
        with open ('/home/pi/config/server_config.csv') as f:
            reader = csv.reader(f)
            for row in reader:
                id_info.append(row)
        filename =  "/home/pi/data/"+"_".join(row)+"_air_quality"+file_time+".csv"
        f = open(filename, "ab+")
        results = csv.writer(open(filename, "ab+"), delimiter = ",")
        metadata = ["Time", "0.3 um", "0.5 um", "1.0 um", "2.5 um", "5.0 um", "10 um", "PM 1.0", "PM 2.5", "PM 10"]
        results.writerow(metadata)
        self.port = serial.Serial("/dev/serial0", baudrate=9600, timeout=1.5)
        
    def start(self):
        global results
        global f
        date_time = datetime.datetime.now()
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

            self.merge_test = False
            self.add_data(self.PM01_queue,self.PM01_list,int(PM01Val),self.PM01_error)
            self.add_data(self.PM25_queue,self.PM25_list,int(PM25Val),self.PM25_error)
            self.add_data(self.PM10_queue,self.PM10_list,int(PM10Val),self.PM10_error)
            self.add_data(self.P3_queue,self.P3_list,int(P3))
            self.add_data(self.P5_queue,self.P5_list,int(P5))
            self.add_data(self.P10_queue,self.P10_list,int(P10))
            self.add_data(self.P25_queue,self.P25_list,int(P25))
            self.add_data(self.P50_queue,self.P50_list,int(P50))
            self.add_data(self.P100_queue,self.P100_list,int(P100))
            self.add_time(self.time_queue, self.time_list, date_time)

            if self.merge_test==True:
                self.PM01_list=[]
                self.PM25_list=[]
                self.PM10_list=[]
                self.P3_list=[]
                self.P5_list=[]
                self.P10_list=[]
                self.P25_list=[]
                self.P50_list=[]
                self.P100_list=[]
                self.time_list=[]

            if self.first_data and len(self.PM01_queue) != 0:
                for i in range(len(self.PM01_queue)):
                    data = []
                    data.append(self.time_queue[i])
                    data.append(self.PM01_queue[i])
                    data.append(self.PM25_queue[i])
                    data.append(self.PM10_queue[i])
                    data.append(self.P3_queue[i])
                    data.append(self.P5_queue[i])
                    data.append(self.P10_queue[i])
                    data.append(self.P25_queue[i])
                    data.append(self.P50_queue[i])
                    data.append(self.P100_queue[i])

                    results.writerow(data)

                self.last_time = data[0]
                self.first_data = False
            elif not self.first_data:
                try:
                    print(self.last_time)
                    if self.time_queue[-1] != self.last_time:
                        data = []
                        data.append(self.time_queue[-1])
                        data.append(self.PM01_queue[-1])
                        data.append(self.PM25_queue[-1])
                        data.append(self.PM10_queue[-1])
                        data.append(self.P3_queue[-1])
                        data.append(self.P5_queue[-1])
                        data.append(self.P10_queue[-1])
                        data.append(self.P25_queue[-1])
                        data.append(self.P50_queue[-1])
                        data.append(self.P100_queue[-1])
                        results.writerow(data)

                        self.last_time = self.time_queue[-1]
                    else:
                        print('duplicated data.')
                except IndexError:
                    print('No new data being written.')
            else: 
                print('No data acquired yet.')

    def close_file(self):
        global f
        f.close()


            
    def pmplot(self):
        if len(self.time_queue)>0:
            self.update_plot(1,self.time_queue,"Time","Particulate Concentration","Particulates vs. time",self.PM01_queue,self.PM25_queue,self.PM10_queue,self.PM01_error,self.PM25_error,self.PM10_error)        

    def add_time(self, queue, timelist, data):
        timelist.append(data)
        if len(timelist)>=self.n_merge:
            self.merge_test=True
            queue.append(timelist[int((self.n_merge)/2)])
            timelist=[]
        if len(queue)>self.maxdata:
            queue.popleft()

    def add_data(self, queue, datalist, data,queue_error=None):
        datalist.append(data)
        if len(datalist)>=self.n_merge:
            queue.append(np.mean(np.asarray(datalist)))
            if queue_error is not None:
            	queue_error.append(np.std(np.asarray(datalist)))
            datalist = []
        if len(queue)>self.maxdata:
            queue.popleft()

    def update_plot(self,plot_id,xdata,xlabel,ylabel,title,ydata1,ydata2=None,ydata3=None,yerr1 = None, yerr2 = None, yerr3 = None):
        #print("\n\n\n")
        #print("Number of time entries = {}".format(len(xdata)))
        #print("Number of PM1 entries = {}".format(len(ydata1)))
        #print("\n\n\n")
        plt.ion()
        fig = plt.figure(plot_id)
        plt.clf()

        gs = GridSpec(6,2)
        ax1 = fig.add_subplot(gs[0,0])
        ax2 = fig.add_subplot(gs[0,1])
        ax3 = fig.add_subplot(gs[1:5,:])

        ax1.set_axis_off()
        ax2.set_axis_off()

        display2_5 = ydata2[-1]
        display_10 = ydata3[-1]
        if display_10 <= 12:
            ax1.text(0.5, 0.6,"PM 10: (ug/m^3)"+ str(display_10), fontsize = 14 , ha = "center", backgroundcolor = "lightgreen")

        elif display_10 > 54 and display_10 <= 154:
            ax1.text(0.5, 0.6,"PM 10: (ug/m^3)"+str(display_10), fontsize = 14, ha = "center", backgroundcolor = "yellow")

        elif display_10 > 154 and display_10 <= 254:
            ax1.text(0.5, 0.6,"PM 10: (ug/m^3)"+str(display_10), fontsize = 14, ha = "center" , backgroundcolor = "orange")

        elif display_10 > 254 and display_10 <= 354:
            ax1.text(0.5, 0.6,"PM 10: (ug/m^3)"+str(display_10), fontsize = 14, ha = "center" , backgroundcolor = "red")

        elif display_10 > 354 and display_10 <= 424:
            ax1.text(0.5, 0.6,"PM 10: (ug/m^3)"+str(display_10), fontsize = 14, ha = "center" , backgroundcolor = "purple")

        else:
            ax1.text(0.5, 0.6,"PM 2.5: (ug/m^3)"+str(display_10), fontsize = 14, ha = "center" , backgroundcolor = "maroon")

        if display2_5 <= 12:
            ax2.text(0.5, 0.6,"PM 2.5: (ug/m^3)"+ str(display2_5), fontsize = 14 , ha = "center", backgroundcolor = "lightgreen")

        elif display2_5 > 12.1 and display_10 <= 35.4:
            ax2.text(0.5, 0.6,"PM 2.5: (ug/m^3)"+str(display2_5), fontsize = 14, ha = "center", backgroundcolor = "yellow")

        elif display2_5 > 35.4 and display_10 <= 55.4:
            ax2.text(0.5, 0.6,"PM 2.5: (ug/m^3)"+str(display2_5), fontsize = 14, ha = "center" , backgroundcolor = "orange")

        elif display2_5 > 55.4 and display_10 <= 150.4:
            ax2.text(0.5, 0.6,"PM 2.5: (ug/m^3)"+str(display2_5), fontsize = 14, ha = "center" , backgroundcolor = "red")

        elif display2_5 > 150.4 and display_10 <= 250.4:
            ax2.text(0.5, 0.6,"PM 2.5: (ug/m^3)"+str(display2_5), fontsize = 14, ha = "center" , backgroundcolor = "purple")

        else:
            ax2.text(0.5, 0.6,"PM 2.5: (ug/m^3)"+str(display2_5), fontsize = 14, ha = "center" , backgroundcolor = "maroon")
        

        ax3.set(xlabel = xlabel, ylabel = ylabel, title = title)
        ax3.plot(xdata,ydata1,"-bo", label='1.0')
        ax3.plot(xdata,ydata2,"-go", label = '2.5')
        ax3.plot(xdata,ydata3,"-ro", label = '10')
        ax3.errorbar(xdata, ydata1, yerr=yerr1)
        ax3.errorbar(xdata, ydata2, yerr=yerr2)
        ax3.errorbar(xdata, ydata3, yerr=yerr3)
        plt.legend(loc="best")
        ax3.xaxis.set_major_formatter(DateFormatter('%H:%M:%S'))
        fig.show()
        plt.pause(0.0005)
        



    