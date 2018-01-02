# -*- coding: utf-8 -*-
"""
Created on Thu Aug  3 15:14:14 2017

@author: Ludi Cao
"""

import matplotlib.pyplot as plt
import csv
import numpy as np
from scipy.stats.stats import pearsonr
import scipy
import dateutil
import datetime

def sublist(datalist, timelist, start, stop):
    timelist2 = np.asarray(timelist)
    datalist2 = np.asarray(datalist)
    indices = np.where((timelist2>start) & (timelist2<stop))
    datalist2 = datalist2[indices]
    timelist2 = timelist2[indices]
    return datalist2.tolist(), timelist2.tolist()


userfile_CO2 = input("CO2 File: ")
userfile_aq =input("Air Quality File: ") 
results_CO2 = csv.reader(open(userfile_CO2), delimiter=',')
results_aq = csv.reader(open(userfile_aq), delimiter=',')

timesCO2 = []
timesaq = []
CO2 = []
aq = []
row_counter1 = 0
row_counter2 = 0

for r in results_CO2:
    row_counter1 += 1
    if row_counter1>1:
        CO2.append(int(r[1]))
        timesCO2.append(dateutil.parser.parse(r[0]))
        
for r in results_aq:
    row_counter2 += 1
    if row_counter2>1:
        aq.append(float(r[8]))
        timesaq.append(dateutil.parser.parse(r[0]))

start1 = datetime.datetime(2017, 7, 27, 16, 00, 00) 
stop1 = datetime.datetime(2017, 7, 28, 2, 00, 00)
CO2, timesCO2 = sublist(CO2, timesCO2, start1, stop1)
aq, timesaq = sublist(aq, timesaq, start1, stop1)

if len(aq)>len(CO2):
    minlist = CO2
if len(CO2)>len(aq):
    minlist = aq
        
n_merge = int(input("n data points to combine:"))
ndata = len(minlist)
nsum_data = int(ndata/n_merge)

CO2_ave = []
CO2_unc = []
aq_ave = []
aq_unc = []


for i in range(nsum_data):
    idata1 = CO2[i*n_merge:(i+1)*n_merge]
    idata_array1 = np.asarray(idata1)
    CO2mean = np.mean(idata_array1)
    CO2sigma = np.sqrt(np.var(idata_array1))
    CO2_ave.append(CO2mean)
    CO2_unc.append(CO2sigma)
    idata2 = aq[i*n_merge:(i+1)*n_merge]
    idata_array2 = np.asarray(idata2)
    aq_mean = np.mean(idata_array2)
    aq_sigma = np.sqrt(np.var(idata_array2))
    aq_ave.append(aq_mean)
    aq_unc.append(aq_sigma)

a = pearsonr(CO2_ave, aq_ave)
b = scipy.stats.spearmanr(CO2_ave, aq_ave)
print("Pearson r =", a[0])
print("P value =", a[1])
print("Spearman r =", b[0])
print("Spearman r=", b[1])

fig = plt.figure()
ax = fig.add_subplot(111)
plt.plot(CO2_ave, aq_ave, "b.")
plt.title("Air Quality vs CO2")
plt.xlabel("CO2 (ppm)")
plt.ylabel("Particle Concentration")
plt.legend()
plt.text(0.6, 0.95, '%s %s' % ("Pearson r =",a[0]), ha='center', va='center', transform = ax.transAxes)
plt.text(0.6, 0.85, '%s %s' % ("P value =",a[1]), ha='center', va='center', transform = ax.transAxes)
plt.text(0.6, 0.75, '%s %s' % ("Spearman r =",b[0]), ha='center', va='center', transform = ax.transAxes)
plt.text(0.6, 0.65, '%s %s' % ("P value =",b[1]), ha='center', va='center', transform = ax.transAxes)
plt.show()