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
from appJar import gui
import numpy as np
import dateutil
from matplotlib.dates import DateFormatter
import matplotlib.pyplot as plt
from collections import deque

class weather_DAQ(object):
    def __init__(self):
        self.sensor = BME280(t_mode=BME280_OSAMPLE_8, p_mode=BME280_OSAMPLE_8, h_mode=BME280_OSAMPLE_8)
        self.running=False
        self.time_queue=deque()
        self.temp_queue=deque()
        self.humid_queue=deque()
        self.press_queue=deque()
        self.maxdata=10
        self.n_merge=5
        self.temp_list=[]
        self.humid_list=[]
        self.press_list=[]
        self.time_list=[]
        self.merge_test=False
        
    def close(self,plot_id):
        plt.close(plot_id)
        
    def create_file(self):
        global results
        file_time= time.strftime("%Y-%m-%d_%H-%M-%S", time.gmtime())
        filename = "weather_test_results_"+file_time+".csv"
        results=csv.writer(open(filename, "ab+"), delimiter = ",")
        metadata=["Time", "Temp (C)","Pressure (hPa)", "Humidity (%)"]
        results.writerow(metadata)

    def start(self):
        global results
        date_time = datetime.datetime.now()
        degrees = self.sensor.read_temperature()
        pascals = self.sensor.read_pressure()
        hectopascals = pascals / 100
        humidity = self.sensor.read_humidity()

        print ('Temp     = {0:0.3f} deg C'.format(degrees))
        print ('Pressure  = {0:0.2f} hPa'.format(hectopascals))
        print ('Humidity = {0:0.2f} %'.format(humidity))
    
        data=[]
        data.append(date_time)
        data.append(degrees)
        data.append(hectopascals)
        data.append(humidity)
    
        results.writerow(data)

        self.merge_test=False
        self.add_data(self.temp_queue,self.temp_list,degrees)
        self.add_data(self.humid_queue,self.humid_list,humidity)
        self.add_data(self.press_queue,self.press_list,hectopascals)
        self.add_time(self.time_queue, self.time_list, date_time)
        
        if self.merge_test==True:
            self.temp_list=[]
            self.humid_list=[]
            self.press_list=[]
            self.time_list=[]
            
    def press(self):
        if len(self.time_queue)>0:
            self.update_plot(3,self.time_queue,self.press_queue,"Time","Pressure(hPa)","Pressure vs. time")
        
    def temp(self):
        if len(self.time_queue)>0:
            self.update_plot(1,self.time_queue,self.temp_queue,"Time","Temperature(C)","Temperature vs. time")
                
    def humid(self):
        if len(self.time_queue)>0:
            self.update_plot(2,self.time_queue,self.humid_queue,"Time","Humidity(%)","Humidity vs.time")


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
        

    def add_data(self, queue, temp_list, data):
        temp_list.append(data)
        if len(temp_list)>=self.n_merge:
            queue.append(np.mean(np.asarray(temp_list)))
            temp_list = []
        if len(queue)>self.maxdata:
            queue.popleft()
    
    def update_plot(self,plot_id,xdata,ydata,xlabel,ylable,title):
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
        fig.show()
        plt.pause(0.0005)

class plotdata(object):
    def __init__(self):
        self.times=[]
        self.times2=[]
        self.times3=[]
        self.degrees_list=[]
        self.pressure_list=[]
        self.humidity_list=[]
        self.temp_ave=[]
        self.temp_unc = []
        self.pressure_ave=[]
        self.pressure_unc=[]
        self.humidity_ave=[]
        self.humidity_unc=[]
        self.merge_times = []
        self.merge_times2 = []
        self.merge_times3 = []
    def plotdata(self): 
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
            import Tkinter
            top = Tkinter.Tk()
            n_merge=int(app.getEntry("n"))
            user_file=app.getOptionBox("Files")
            results = csv.reader(open(user_file), delimiter=',')          

                    
            def temp():
                row_counter=0              
                for r in results:
                    if row_counter>0:
                        self.times.append(dateutil.parser.parse(r[0]))
                        self.degrees_list.append(float(r[1]))                
                    row_counter+=1
             
                ndata = int(len(self.degrees_list))
                nsum_data = int(ndata/n_merge)
                
                for i in range(nsum_data):
                    itemp = self.degrees_list[i*n_merge:(i+1)*n_merge]
                    itemp_array = np.asarray(itemp)
                    temp_mean = np.mean(itemp_array)
                    temp_sigma = np.sqrt(np.var(itemp_array))
                    self.temp_ave.append(temp_mean)
                    self.temp_unc.append(temp_sigma)
            
                for i in range(nsum_data):
                    itimes = self.times[i*n_merge:(i+1)*n_merge]
                    itime = itimes[int(len(itimes)/2)]
                    self.merge_times.append(itime)

                fig=plt.figure()
                ax=fig.add_subplot(111)   
                plt.plot(self.merge_times, self.temp_ave, "b.")
                plt.errorbar(self.merge_times, self.temp_ave, yerr = self.temp_unc)
                plt.title("Temperature")
                plt.xlabel("Time(s)")
                plt.ylabel("Temperature(C)")
                fig.autofmt_xdate()
                ax.xaxis.set_major_formatter(DateFormatter('%H:%M:%S'))
                plt.show()
            
            def press():
                global ndata
                global nsum_data
                row_counter=0
                for r in results:
                    if row_counter>0:
                        self.times2.append(dateutil.parser.parse(r[0]))
                        self.pressure_list.append(float(r[2]))              
                    row_counter+=1
               
                ndata2 = int(len(self.pressure_list))
                nsum_data2 = int(ndata2/n_merge)
                
                for i in range(nsum_data2):
                    ipressure = self.pressure_list[i*n_merge:(i+1)*n_merge]   
                    ipressure_array = np.asarray(ipressure)
                    pressure_mean = np.mean(ipressure_array)
                    pressure_sigma = np.sqrt(np.var(ipressure_array))
                    self.pressure_ave.append(pressure_mean)
                    self.pressure_unc.append(pressure_sigma)
                    
                for i in range(nsum_data2):
                    itimes2 = self.times2[i*n_merge:(i+1)*n_merge]
                    itime2 = itimes2[int(len(itimes2)/2)]
                    self.merge_times2.append(itime2)

                fig=plt.figure()
                ax=fig.add_subplot(111)
                plt.plot(self.merge_times2, self.pressure_ave,"g." )
                plt.errorbar(self.merge_times2, self.pressure_ave, yerr = self.pressure_unc)
                plt.title("Pressure")
                plt.xlabel("Time(s)")
                plt.ylabel("Pressure(hPa)")
                fig.autofmt_xdate()
                ax.xaxis.set_major_formatter(DateFormatter('%H:%M:%S'))
                plt.show()
        
            def humid():  
                row_counter=0
                for r in results:
                    if row_counter>0:
                        self.times3.append(dateutil.parser.parse(r[0]))
                        self.humidity_list.append(float(r[3]))
                
                    row_counter+=1
                    
                ndata3 = int(len(self.humidity_list))
                nsum_data3 = int(ndata3/n_merge)
                
                for i in range(nsum_data3):
                    ihumid = self.humidity_list[i*n_merge:(i+1)*n_merge]
                    ihumid_array = np.asarray(ihumid)
                    humid_mean = np.mean(ihumid_array)
                    humid_sigma = np.sqrt(np.var(ihumid_array))
                    self.humidity_ave.append(humid_mean)
                    self.humidity_unc.append(humid_sigma)
                    
                for i in range(nsum_data3):
                    itimes3 = self.times3[i*n_merge:(i+1)*n_merge]
                    itime3 = itimes3[int(len(itimes3)/2)]
                    self.merge_times3.append(itime3)
                
                fig=plt.figure()
                ax=fig.add_subplot(111)
                plt.plot(self.merge_times3, self.humidity_ave,"r." )
                plt.errorbar(self.merge_times3, self.humidity_ave, yerr = self.humidity_unc)
                plt.title("Humidity")
                plt.xlabel("Time(s)")
                plt.ylabel("Humidity(%)")
                fig.autofmt_xdate()
                ax.xaxis.set_major_formatter(DateFormatter('%H:%M:%S'))
                plt.show()

            tempButton = Tkinter.Button(top, height=2, width=20, text="Temperature PLot", command=temp)
            pressButton =Tkinter.Button(top, height=2, width=20, text="Pressure Plot", command=press)
            humidButton = Tkinter.Button(top, height=2, width=20, text="Humidity Plot", command=humid)
            
            tempButton.pack()
            pressButton.pack()
            humidButton.pack()
            
            top.mainloop()
            
        app.addButton("OK",ok)
        app.setButtonWidth("OK","20")
        app.setButtonHeight("OK","4")
        app.setButtonFont("20","Helvetica")
        app.go()

       
            
     
                
            
        


    


        