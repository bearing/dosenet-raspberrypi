# -*- coding: utf-8 -*-
"""
Created on Thu Jul 27 10:40:06 2017

@author: Ludi Cao
"""

import matplotlib.pyplot as plt
import csv
import numpy as np
from scipy.stats.stats import pearsonr
import scipy

userfile_CO2 = input("CO2 File: ") 
userfile_Humid =input("Humidity File: ") 
results_CO2 = csv.reader(open(userfile_CO2), delimiter=',')
results_Humid = csv.reader(open(userfile_Humid), delimiter=',')

CO2 = []
Humidity = []
row_counter1 = 0
row_counter2 = 0

for r in results_CO2:
	row_counter1 += 1
	if row_counter1>1:
		CO2.append(int(r[1]))
        
for r in results_Humid:
	row_counter2 += 1
	if row_counter2>1:
		Humidity.append(float(r[3]))
        
n_merge = int(input("n data points to combine:"))
ndata = len(CO2)
nsum_data = int(ndata/n_merge)

CO2_ave = []
CO2_unc = []
Humid_ave = []
Humid_unc = []

for i in range(nsum_data):
	idata1 = CO2[i*n_merge:(i+1)*n_merge]
	idata_array1 = np.asarray(idata1)
	CO2mean = np.mean(idata_array1)
	CO2sigma = np.sqrt(np.var(idata_array1))
	CO2_ave.append(CO2mean)
	CO2_unc.append(CO2sigma)
	idata2 = Humidity[i*n_merge:(i+1)*n_merge]
	idata_array2 = np.asarray(idata2)
	Humidity_mean = np.mean(idata_array2)
	Humidity_sigma = np.sqrt(np.var(idata_array2))
	Humid_ave.append(Humidity_mean)
	Humid_unc.append(Humidity_sigma)
    

a = pearsonr(CO2_ave, Humid_ave)
b = scipy.stats.spearmanr(CO2_ave, Humid_ave)
print("Pearson r =", a[0])
print("P value =", a[1])
print("Spearman r =", b[0])
print("Spearman r=", b[1])    
    
fig = plt.figure()
ax = fig.add_subplot(111)
plt.plot(CO2_ave, Humid_ave, "b.")
plt.title("Humidity vs CO2")
plt.xlabel("CO2 (ppm)")
plt.ylabel("Humidity (%)")
plt.legend()
plt.text(0.6, 0.95, '%s %s' % ("Pearson r =",a[0]), ha='center', va='center', transform = ax.transAxes)
plt.text(0.6, 0.85, '%s %s' % ("P value =",a[1]), ha='center', va='center', transform = ax.transAxes)
plt.text(0.6, 0.75, '%s %s' % ("Spearman r =",b[0]), ha='center', va='center', transform = ax.transAxes)
plt.text(0.6, 0.65, '%s %s' % ("P value =",b[1]), ha='center', va='center', transform = ax.transAxes)
plt.show()


    
    
