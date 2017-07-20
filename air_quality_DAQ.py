# July 18th, 2017 15:49
# Code by Jennifer Atkins
# Based off of code by Ludi Cao

import time
import datetime
import csv
import numpy as np
from matplotlib.dates import DateFormatter
import matplotlib.pyplot as plt
from collections import deque
import serial

#sensor = entercodehere(morestuff) [Not sure if this is necessary] 

class air_quality_DAQ(object):
    def __init__ (self):
        # self.sensor = sensor [Not sure if this is necessary]
        self.running = False
        self.time_queue = deque()
        self.PM01_queue = deque()
        self.PM25_queue = deque()
        self.PM10_queue = deque()
        self.P3_queue = deque()
        self.P5_queue = deque()
        self.P10_queue = deque()
        self.P25_queue = deque()
        self.P50_queue = deque()
        self.P100_queue = deque()
        self.maxdata = 10
        self.n_merge = 5
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
    
    def close(self,plot_id):
        plt.close(plot_id)

    def create_file(self):
        global results
        file_time = time.strftime("%Y-%m-%d_%H-%M-%S", time.gmtime())
        filename = "/home/pi/data/air_quality_test_results_"+file_time+".csv"
        results = csv.writer(open(filename, "ab+"), delimiter = ",")
        metadata = ["Time", "0.3 um", "0.5 um", "1.0 um", "2.5 um", "5.0 um", "10 um", "PM 1.0", "PM 2.5", "PM 10"]
        results.writerow(metadata)

    def start(self):
        global results
        date_time = datetime.datetime.now()
        port = serial.Serial("/dev/ttyS0", baudrate=9600, timeout=1.5)
        text = port.read(32)
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

            print('\nConcentration of Particulate Matter [ug/m3]\n')
            print('PM 1.0 = {} ug/m3'.format(PM01Val))
            print('PM 2.5 = {} ug/m3'.format(PM25Val))
            print('PM 10  = {} ug/m3'.format(PM25Val))

            # Print number of particles in 0.1 L of air over specific diamaters
            print('Number of particles in 0.1 L of air with specific diameter\n')
            print('#Particles, diameter over 0.3 um = {}'.format(P3))
            print('#Particles, diameter over 0.5 um = {}'.format(P5))
            print('#Particles, diameter over 1.0 um = {}'.format(P10))
            print('#Particles, diameter over 2.5 um = {}'.format(P25))
            print('#Particles, diameter over 5.0 um = {}'.format(P50))
            print('#Particles, diameter over 10  um = {}'.format(P100))

            data = []
            data.append(date_time)
            data.append(PM01Val)
            data.append(PM25Val)
            data.append(PM10Val)
            data.append(P3)
            data.append(P5)
            data.append(P10)
            data.append(P25)
            data.append(P50)
            data.append(P100)

            results.writerow(data)

            self.merge_test = False
            self.add_data(self.PM01_queue,self.PM01_list,int(PM01Val))
            self.add_data(self.PM25_queue,self.PM25_list,int(PM25Val))
            self.add_data(self.PM10_queue,self.PM10_list,int(PM10Val))
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
            
    def pmplot(self):
        if len(self.time_queue)>0:
            self.update_plot(1,self.time_queue,"Time","Particulate Concentration","Particulates vs. time",self.PM01_queue,self.PM25_queue,self.PM10_queue)        

    def add_time(self, queue, timelist, data):
        print('Input time: {}'.format(data))
        timelist.append(data)
        if len(timelist)>=self.n_merge:
            self.merge_test=True
            queue.append(timelist[int((self.n_merge)/2)])
            print('Queue time: {}'.format(timelist[int((self.n_merge)/2)]))
            timelist=[]
        if len(queue)>self.maxdata:
            queue.popleft()

    def add_data(self, queue, datalist, data):
        datalist.append(data)
        if len(datalist)>=self.n_merge:
            queue.append(np.mean(np.asarray(datalist)))
            datalist = []
        if len(queue)>self.maxdata:
            queue.popleft()

    def update_plot(self,plot_id,xdata,xlabel,ylable,title,ydata1,ydata2=None,ydata3=None):
        plt.ion()
        fig = plt.figure(plot_id)
        plt.clf()
        ax=fig.add_subplot(111)
        plt.xlabel(xlabel)
        plt.ylabel(ylable) 
        plt.title(title)
        plt.plot(xdata,ydata1,"b.", label='1.0')
        plt.plot(xdata,ydata2,"g.", label = '2.5')
        plt.plot(xdata,ydata3,"r.", label = '10')
        plt.legend(loc="best")
        fig.autofmt_xdate()
        ax.xaxis.set_major_formatter(DateFormatter('%H:%M:%S'))
        fig.show()
        plt.pause(0.0005)



    