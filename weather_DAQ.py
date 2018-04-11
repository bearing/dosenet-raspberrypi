# -*- coding: utf-8 -*-
"""
Created on Wed Jul 12 11:32:41 2017

@author: Ludi Cao
"""
import time
import datetime
import csv
from Adafruit_BME280 import *
import os
import numpy as np
import dateutil
from matplotlib.dates import DateFormatter
import matplotlib.pyplot as plt
from collections import deque

class weather_DAQ(object):
    def __init__(self, maxdata, n_merge):
        self.sensor = None
        self.running=False
        self.time_queue=deque()
        self.temp_queue=deque()
        self.humid_queue=deque()
        self.press_queue=deque()
        self.temp_err=deque()
        self.humid_err=deque()
        self.press_err=deque()
        self.maxdata=int(maxdata)
        self.n_merge=int(n_merge)
        self.temp_list=[]
        self.humid_list=[]
        self.press_list=[]
        self.time_list=[]
        self.merge_test=False
        self.first_data = True
        self.last_time = None

    def close(self,plot_id):
        plt.close(plot_id)
        
    def create_file(self):
        global results
        self.sensor = BME280(t_mode=BME280_OSAMPLE_8, p_mode=BME280_OSAMPLE_8, h_mode=BME280_OSAMPLE_8)        
        file_time= time.strftime("%Y-%m-%d_%H-%M-%S", time.gmtime())
        filename = "/home/pi/data/weather_test_results_"+file_time+".csv"
        results=csv.writer(open(filename, "ab+"), delimiter = ",")
        metadata=["Time", "Temp (C)","Temp SD","Pressure (hPa)", "Pressure SD","Humidity (%)","Humidity SD"]
        results.writerow(metadata)

    def start(self):
        global results
        date_time = datetime.datetime.now()
        degrees = self.sensor.read_temperature()
        pascals = self.sensor.read_pressure()
        hectopascals = pascals / 100
        humidity = self.sensor.read_humidity()
    
        data=[]

        self.merge_test=False
        self.add_data(self.temp_queue,self.temp_err,self.temp_list,degrees)
        self.add_data(self.humid_queue,self.humid_err,self.humid_list,humidity)
        self.add_data(self.press_queue,self.press_err,self.press_list,hectopascals)
        self.add_time(self.time_queue,self.time_list, date_time)
        
        # data.append(date_time)
        # data.append(degrees)
        # data.append(hectopascals)
        # data.append(humidity)
    
        # results.writerow(data)         

        if self.first_data and len(self.temp_queue) != 0:
            for i in range(len(self.temp_queue)):
                data = []
                data.append(self.time_queue[i])
                data.append(self.temp_queue[i])
                data.append(self.temp_err[i])
                data.append(self.press_queue[i])
                data.append(self.press_err[i])
                data.append(self.humid_queue[i])
                data.append(self.humid_err[i])
                results.writerow(data)

            self.last_time = data[0]
            self.first_data = False
        elif not self.first_data:
            try:
                print(self.last_time)
                if self.time_queue[-1] != self.last_time:
                    data = []
                    data.append(self.time_queue[-1])
                    data.append(self.temp_queue[-1])
                    data.append(self.temp_err[-1])
                    data.append(self.press_queue[-1])
                    data.append(self.press_err[-1])
                    data.append(self.humid_queue[-1])
                    data.append(self.humid_err[-1])
                    results.writerow(data)

                    self.last_time = self.time_queue[-1]
                else:
                    print('duplicated data.')
            except IndexError:
                print('No new data being written.')
        else: 
            print('No data acquired yet.')

        print ('Temp     = {0:0.3f} deg C'.format(degrees))
        print ('Pressure  = {0:0.2f} hPa'.format(hectopascals))
        print ('Humidity = {0:0.2f} %\n'.format(humidity))
        
        
    def press(self):
        if len(self.time_queue)>0:
            self.update_plot(3,self.time_queue,self.press_queue,self.press_err,"Time","Pressure(hPa)","Pressure vs. time")
        
    def temp(self):
        if len(self.time_queue)>0:
            self.update_plot(1,self.time_queue,self.temp_queue,self.temp_err,"Time","Temperature(C)","Temperature vs. time")
                
    def humid(self):
        if len(self.time_queue)>0:
            self.update_plot(2,self.time_queue,self.humid_queue,self.humid_err,"Time","Humidity(%)","Humidity vs.time")


    def add_time(self, queue, timelist, data):
        print('Input time: {}\n'.format(data))
        timelist.append(data)

        if len(timelist)>=self.n_merge:
            self.merge_test=True
            queue.append(timelist[int((self.n_merge)/2)])
            print('Queue time: {}\n'.format(timelist[int((self.n_merge)/2)]))
            for i in range(len(timelist)):
                timelist.pop()
        if len(queue)>self.maxdata:
            queue.popleft()
        

    def add_data(self, queue, queue_err,temp_list, data):
        temp_list.append(data)
        if len(temp_list)>=self.n_merge:
            queue.append(np.mean(np.asarray(temp_list)))
            queue_err.append(np.std(np.asarray(temp_list)))
            for i in range(len(temp_list)):
                temp_list.pop()
        if len(queue)>self.maxdata:
            queue.popleft()
    
    def update_plot(self,plot_id,xdata,ydata,yerr,xlabel,ylable,title):
        plt.ion()
        fig = plt.figure(plot_id)
        plt.clf()
        ax=fig.add_subplot(111)
        plt.xlabel(xlabel)
        plt.ylabel(ylable) 
        plt.title(title)
        plt.plot(xdata,ydata,"r.")
        fig.autofmt_xdate()
        ax.xaxis.set_major_formatter(DateFormatter('%H:%M:%S'))
        ax.errorbar(xdata, ydata, yerr=yerr)
        fig.show()
        plt.pause(0.0005)

    def plotdata(self):
        
        times=[]
        degrees_list=[]
        pressure_list=[]
        humidity_list=[]
        temp_ave=[]
        temp_unc = []
        pressure_ave=[]
        pressure_unc=[]
        humidity_ave=[]
        humidity_unc=[]
        merge_times = []
        
        app=gui("Weather Plot","800x400")   
        app.addLabel("1","Please choose a following .csv file")
        file_name=[]
        for filename in os.listdir('.'):
            if filename.endswith(".csv"):
                file_name.append(os.path.join('.', filename))
        app.setFont(20)
        app.addOptionBox("Files",file_name)
        app.setOptionBoxHeight("Files","4")
        app.addLabel("2","Enter the number of data points to merge:")
        app.setLabelFont("20","Heletica")
        app.addNumericEntry("n")
        app.setFocus("n")     
    
        def ok(btn):
            user_file=app.getOptionBox("Files") 
            n_merge=int(app.getEntry("n"))
            row_counter=0
            results = csv.reader(open(user_file), delimiter=',')


            for r in results:
                if row_counter>0:
                    times.append(dateutil.parser.parse(r[0]))
                    degrees_list.append(float(r[1]))
                    pressure_list.append(float(r[2]))
                    humidity_list.append(float(r[3]))
        
                row_counter+=1

            ndata = int(len(degrees_list))
            nsum_data = int(ndata/n_merge)

            for i in range(nsum_data):
                itemp = degrees_list[i*n_merge:(i+1)*n_merge]
                itemp_array = np.asarray(itemp)
                temp_mean = np.mean(itemp_array)
                temp_sigma = np.sqrt(np.var(itemp_array))
                temp_ave.append(temp_mean)
                temp_unc.append(temp_sigma)
    
            for i in range(nsum_data):
                ipressure = pressure_list[i*n_merge:(i+1)*n_merge]   
                ipressure_array = np.asarray(ipressure)
                pressure_mean = np.mean(ipressure_array)
                pressure_sigma = np.sqrt(np.var(ipressure_array))
                pressure_ave.append(pressure_mean)
                pressure_unc.append(pressure_sigma)
    
            for i in range(nsum_data):
                ihumid = humidity_list[i*n_merge:(i+1)*n_merge]
                ihumid_array = np.asarray(ihumid)
                humid_mean = np.mean(ihumid_array)
                humid_sigma = np.sqrt(np.var(ihumid_array))
                humidity_ave.append(humid_mean)
                humidity_unc.append(humid_sigma)

            for i in range(nsum_data):
                itimes = times[i*n_merge:(i+1)*n_merge]
                itime = itimes[int(len(itimes)/2)]
                merge_times.append(itime)
            fig=plt.figure()
            ax=fig.add_subplot(111)   
            plt.plot(merge_times, temp_ave, "b.")
            plt.errorbar(merge_times, temp_ave, yerr = temp_unc)
            plt.title("Temperature")
            plt.xlabel("Time(s)")
            plt.ylabel("Temperature(C)")
            fig.autofmt_xdate()
            ax.xaxis.set_major_formatter(DateFormatter('%H:%M:%S'))

            fig=plt.figure()
            ax=fig.add_subplot(111)
            plt.plot(merge_times, pressure_ave,"g." )
            plt.errorbar(merge_times, pressure_ave, yerr = pressure_unc)
            plt.title("Pressure")
            plt.xlabel("Time(s)")
            plt.ylabel("Pressure(hPa)")
            fig.autofmt_xdate()
            ax.xaxis.set_major_formatter(DateFormatter('%H:%M:%S'))

            fig=plt.figure()
            ax=fig.add_subplot(111)
            plt.plot(merge_times, humidity_ave,"r." )
            plt.errorbar(merge_times, humidity_ave, yerr = humidity_unc)
            plt.title("Humidity")
            plt.xlabel("Time(s)")
            plt.ylabel("Humidity(%)")
            fig.autofmt_xdate()
            ax.xaxis.set_major_formatter(DateFormatter('%H:%M:%S'))
            plt.show()
    
        app.addButton("OK",ok)
        app.setButtonWidth("OK","20")
        app.setButtonHeight("OK","4")
        app.setButtonFont("20","Helvetica")
        app.go()
