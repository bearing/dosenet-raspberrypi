# -*- coding: utf-8 -*-
"""
Created on Thu Jun 29 15:31:03 2017

@author: Ludi Cao
"""


import matplotlib.pyplot as plt
import csv
import dateutil
import datetime
import numpy as np
from matplotlib.dates import DateFormatter

    
def time_sublist(datalist, timelist, start, stop):
    timelist2 = np.asarray(timelist)
    indices = np.where((timelist2>start) & (timelist2<stop))
    datalist2 = np.asarray(datalist)
    datalist2 = datalist2[indices]
    timelist2 = timelist2[indices]
    return datalist2.tolist(), timelist2.tolist()

times=[]
degrees_list=[]
pressure_list=[]
humidity_list=[]
row_counter=0


userfile_Weather = input("Weather File: ")
results = csv.reader(open(userfile_Weather), delimiter=',')

for r in results:
    if row_counter>0:
        times.append(dateutil.parser.parse(r[0]))
        degrees_list.append(float(r[1]))
        pressure_list.append(float(r[2]))
        humidity_list.append(float(r[3]))
        
    row_counter+=1

        
start1 = datetime.datetime(2017, 8, 2, 10, 00, 00) 
stop1 = datetime.datetime(2017, 8, 3, 00, 00, 00)
degrees_list, times1 = time_sublist(degrees_list, times, start1, stop1)
pressure_list, times1 = time_sublist(pressure_list, times, start1, stop1)
humidity_list, times1 = time_sublist(humidity_list, times, start1, stop1)
times = times1
    
temp_ave=[]
temp_unc = []
pressure_ave=[]
pressure_unc=[]
humidity_ave=[]
humidity_unc=[]
merge_times = []

n_merge = int(input("n data points to combine:"))
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
ax.xaxis.set_major_formatter(DateFormatter('%d-%m-%y %H:%M:%S'))


fig=plt.figure()
ax=fig.add_subplot(111)
plt.plot(merge_times, pressure_ave,"g." )
plt.errorbar(merge_times, pressure_ave, yerr = pressure_unc)
plt.title("Pressure")
plt.xlabel("Time(s)")
plt.ylabel("Pressure(hPa)")
fig.autofmt_xdate()
ax.xaxis.set_major_formatter(DateFormatter('%d-%m-%y %H:%M:%S'))


fig=plt.figure()
ax=fig.add_subplot(111)
plt.plot(merge_times, humidity_ave,"r." )
plt.errorbar(merge_times, humidity_ave, yerr = humidity_unc)
plt.title("Humidity")
plt.xlabel("Time(s)")
plt.ylabel("Humidity(%)")
fig.autofmt_xdate()
ax.xaxis.set_major_formatter(DateFormatter('%d-%m-%y %H:%M:%S'))
plt.show()

