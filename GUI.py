# -*- coding: utf-8 -*-
"""
Created on Fri Jul  7 14:44:14 2017

@author: Ludi Cao
"""

from appJar import gui
import os

app = gui("Adafruit Weather Sensor", "800x400")
import matplotlib.pyplot as plt
import dateutil
import numpy as np
from matplotlib.dates import DateFormatter
import time
import datetime
import csv
from Adafruit_BME280 import *

sensor = BME280(t_mode=BME280_OSAMPLE_8, p_mode=BME280_OSAMPLE_8, h_mode=BME280_OSAMPLE_8)

file_time= time.strftime("%Y-%m-%d_%H-%M-%S", time.gmtime())
filename = "weather_test_results_"+file_time+".csv"

def weather_test(btn):
    app=gui("Weather Test","800x400")
    app.addLabelNumericEntry("seconds","Number of Seconds")
    app.setFocus("seconds")
    def n(btn):
        time_of_program=app.getEntry("seconds")
        results=csv.writer(open(filename, "ab+"), delimiter = ",")

        metadata=["Time", "Temp (C)","Pressure (hPa)", "Humidity (%)"]
        results.writerow(metadata)
        time_passed=0
    
        while time_passed<time_of_program:
            date_time = datetime.datetime.now()
            degrees = sensor.read_temperature()
            pascals = sensor.read_pressure()
            hectopascals = pascals /100
            humidity = sensor.read_humidity()

            print ('Temp     = {0:0.3f} deg C'.format(degrees))
            print ('Pressure  = {0:0.2f} hPa'.format(hectopascals))
            print ('Humidity = {0:0.2f} %'.format(humidity))
    
            data=[]
            data.append(date_time)
            data.append(degrees)
            data.append(hectopascals)
            data.append(humidity)
    
            results.writerow(data)
    
            time.sleep(1)
    
            time_passed+=1

    app.addButton("OK",n)      
    app.go() 
    
def weather_plot(btn):
    app=gui("Weather Plot","800x400")
    times=[]
    degrees_list=[]
    pressure_list=[]
    humidity_list=[]

    file_name=[]
    for filename in os.listdir('.'):
        if filename.endswith(".csv"):
            file_name.append(os.path.join('.', filename))
    app.setFont(20)
    app.addOptionBox("Files",file_name)
    app.addLabelNumericEntry("n","n data points to combine")
    app.setFocus("n")
    
    def ok(btn):
        user_file=app.getOptionBox("Files")
        row_counter=0
        results = csv.reader(open(user_file), delimiter=',')

        for r in results:
            if row_counter>0:
                times.append(dateutil.parser.parse(r[0]))
                degrees_list.append(float(r[1]))
                pressure_list.append(float(r[2]))
                humidity_list.append(float(r[3]))
        
                row_counter+=1
    
        temp_ave=[]
        temp_unc = []
        pressure_ave=[]
        pressure_unc=[]
        humidity_ave=[]
        humidity_unc=[]
        merge_times = []

        n_merge = app.getEntry("n")
        ndata = len(degrees_list)
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
    app.go()
    
    

app.addButton("Record Weather Data", weather_test)
app.addButton("Plot Weather Data",weather_plot)
app.go()
