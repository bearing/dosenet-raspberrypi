# -*- coding: utf-8 -*-
"""
Created on Wed Jul 12 11:32:41 2017

@author: Ludi Cao
"""
import time
import datetime
import csv
from Adafruit_BME280 import *

sensor = BME280(t_mode=BME280_OSAMPLE_8, p_mode=BME280_OSAMPLE_8, h_mode=BME280_OSAMPLE_8)

class weather_DAQ(object):
    def __init__(self):
        self.sensor = sensor
        self.running=False
        
    def open_file(self):
        global results
        file_time= time.strftime("%Y-%m-%d_%H-%M-%S", time.gmtime())
        filename = "weather_test_results_"+file_time+".csv"
        results=csv.writer(open(filename, "ab+"), delimiter = ",")
        metadata=["Time", "Temp (C)","Pressure (hPa)", "Humidity (%)"]
        results.writerow(metadata)

    def start(self):
        global job1
        global results
        date_time = datetime.datetime.now()
        degrees = sensor.read_temperature()
        pascals = sensor.read_pressure()
        hectopascals = pascals / 100
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
        job1=top.after(1000,start)
    
    def stop(self):
        global job1
        top.after_cancel(job1)
        