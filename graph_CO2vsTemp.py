import matplotlib.pyplot as plt
from matplotlib import style
import csv
import dateutil
import time
import datetime
import numpy as np
from matplotlib.dates import date2num, DateFormatter
from scipy.stats.stats import spearmanr

def get_covariance(x_data, y_data):
	x_sigma = np.sqrt(np.var(x_data))
	y_sigma = np.sqrt(np.var(y_data))
	x_mean = np.mean(x_data)
	y_mean = np.mean(y_data)

	xy_sum = 0
	for i in range(len(x_data)):
		xy_sum = xy_sum + (x_data[i]-x_mean)*(y_data[i]-y_mean)
	correlation_coef = xy_sum / ((x_sigma)*(y_sigma)) / len(x_data)
	return correlation_coef	

userfile_CO2 = input("CO2 File Name: ")
userfile_temp = input("Weather File Name: ")

results_CO2 = csv.reader(open(userfile_CO2), delimiter=',')
results_temp = csv.reader(open(userfile_temp), delimiter=',')
CO2 = []
temp = []
row_counter1 = 0
row_counter2 = 0
for r in results_CO2:
	row_counter1 += 1
	if row_counter1>1:
		CO2.append(int(r[1]))

for r in results_temp:
	row_counter2 += 1
	if row_counter2>1:
		temp.append(float(r[1]))		

n_merge = int(input("n data points to combine:"))
ndata = len(CO2)
nsum_data = int(ndata/n_merge)
ndata2 = len(temp)
nsum_data2 = int(ndata2/n_merge)

CO2_ave = []
CO2_unc = []
temp_ave = []
temp_unc = []

for i in range(nsum_data):
	idata = CO2[i*n_merge:(i+1)*n_merge]
	idata_array = np.asarray(idata)
	CO2mean = np.mean(idata_array)
	CO2sigma = np.sqrt(np.var(idata_array))
	CO2_ave.append(CO2mean)
	CO2_unc.append(CO2sigma)
for i in range(nsum_data2):	
	idata2 = temp[i*n_merge:(i+1)*n_merge]
	idata_array2 = np.asarray(idata2)
	tempmean = np.mean(idata_array2)
	tempsigma = np.sqrt(np.var(idata_array2))
	temp_ave.append(tempmean)
	temp_unc.append(tempsigma)

CO2_array = np.asarray(CO2_ave)
temp_array = np.asarray(temp_ave)
correlation_coef = get_covariance(CO2_array, temp_array)
print("Correlation:", correlation_coef)

correlation_values = spearmanr(CO2_array, temp_array)
print("p value =", correlation_values[1])

fig = plt.figure()
plt.plot(CO2_ave, temp_ave, "b.")
plt.xlabel("CO2 (ppm)")
plt.ylabel("Temperature (C)")
plt.title("CO2 vs Temperature")
fig.autofmt_xdate()

ax = fig.add_subplot(111)
corr_statement = "Correlation Coefficient =", correlation_coef
p_value = "P Value =", correlation_values[1]
plt.annotate(corr_statement, xy=(0,1), xytext=(12,-12), va='top',
	xycoords='axes fraction', textcoords='offset points')
plt.annotate(p_value, xy=(0,0.94), xytext=(12,-12), va='top',
	xycoords='axes fraction', textcoords='offset points')
	
plt.show()
