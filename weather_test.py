#!/bin/python

import time
import datetime
import csv
import sys
from Adafruit_BME280 import *

sys.stdout.flush()

sensor = BME280(t_mode=BME280_OSAMPLE_8, p_mode=BME280_OSAMPLE_8, h_mode=BME280_OSAMPLE_8)

file_time= time.strftime("%Y-%m-%d_%H-%M-%S", time.gmtime())
filename = "weather_test_results_"+file_time+".csv"
results=csv.writer(open(filename, "ab+"), delimiter = ",")

logfilename = "weather_test_results.csv"
logresults = open(logfilename, "wb+", 0)

metadata=["Time", "Temp (C)","Pressure (hPa)", "Humidity (%)"]
results.writerow(metadata)
logresults.write(metadata[0]+","+metadata[1]+","+metadata[2]+","+metadata[3]+"\n")

while True:
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
    logresults.write(datetime.datetime.strftime(data[0], "%Y-%m-%d %H:%M:%S")+","+str(data[1])+","+str(data[2])+","+str(data[3])+"\n")

    time.sleep(1)
