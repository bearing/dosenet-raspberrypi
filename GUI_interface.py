#!/usr/bin/env/python

from appJar import gui
import os
import matplotlib.pyplot as plt
import dateutil
import numpy as np
from matplotlib.dates import DateFormatter
import time
import datetime
import csv
import weather_DAQ

app = gui("Adafruit Weather Sensor", "800x400")
from Adafruit_BME280 import *

sensor = BME280(t_mode=BME280_OSAMPLE_8, p_mode=BME280_OSAMPLE_8, h_mode=BME280_OSAMPLE_8)

wdaq = weather_DAQ.weather_DAQ()

def weather_test(btn):

    wdaq.open_file()
    wdaq.startstop()


def weather_plot(btn):
    app=gui("Weather Plot","800x400")
    times=[]
    degrees_list=[]
    pressure_list=[]
    humidity_list=[]
    
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
    app.setEntryHeight("n","4")
    
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
    
        temp_ave=[]
        temp_unc = []
        pressure_ave=[]
        pressure_unc=[]
        humidity_ave=[]
        humidity_unc=[]
        merge_times = []

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
    app.setButtonWidth("OK","20")
    app.setButtonHeight("OK","4")
    app.setButtonFont("20","Helvetica")
    app.go()

app.addButton("Record Weather Data", weather_test)
app.setButtonWidth("Record Weather Data", "30")
app.setButtonHeight("Record Weather Data","4")
app.setButtonFont("20",font="Helvetica")
app.addButton("Plot Weather Data",weather_plot)
app.setButtonWidth("Plot Weather Data","30")
app.setButtonHeight("Plot Weather Data","4")
app.setButtonFont("20",font="Helvetica")
app.go()
