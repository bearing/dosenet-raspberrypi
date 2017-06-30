# -*- coding: utf-8 -*-
"""
Created on Thu Jun 29 15:31:03 2017

@author: Ludi Cao
"""

from Adafruit_BME280 import *

import matplotlib.pyplot as plt
import csv
import dateutil
import time
import datetime

times=[]
degrees_list=[]
pressure_list=[]
humidity_list=[]
row_counter=0
user_file = input("What weather test result file do you want to graph? (Put quotation marks around the file name.) File Name: ")

results = csv.reader(open(user_file), delimiter=',')

for r in results:
    if row_counter>0:
        times.append(dateutil.parser.parse(r[0]))
        degrees_list.append(r[1])
        pressure_list.append(r[2])
        humidity_list.append(r[3])
        
    row_counter+=1
    
    
plt.plot(times, degrees_list, "b.")
plt.xlabel("Time(s)")
plt.ylabel("Degrees(C)")
plt.show()

plt.plot(times, pressure_list)
plt.xlabel("Time(s)")
plt.ylabel("Pressure hPa")
plt.show()

plt.plot(times, humidity_list)
plt.xlabel("Time(s)")
plt.ylabel("Humidity(%)")
plt.show()


