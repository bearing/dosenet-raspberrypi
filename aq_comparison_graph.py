#Code by Jennifer Atkins
#Created Tuesday July 25, 2017 13:20:16
#Python file that graphs multiple air quality test result CSV files

import matplotlib.pyplot as plt
import csv
import dateutil
import numpy as np
import time
import datetime

def correlation_coefficient(xdata,ydata):
	xmean = np.mean(xdata)
	ymean = np.mean(ydata)
	xsigma = np.sqrt(np.var(xdata))
	ysigma = np.sqrt(np.var(ydata))
	xysums = 0
	for i in range(len(xdata)):
		xdiff = xdata[i] - xmean
		ydiff = ydata[i] - ymean
		xysums = xdiff * ydiff +xysums
	stnddevs = xsigma * ysigma
	coeff = xysums/stnddevs/len(xdata)
	return coeff

user_file1 = input("File Name 1: ")
resultsa = csv.reader(open(user_file1), delimiter=',')

user_file2 = input("File Name 2: ")
resultsb = csv.reader(open(user_file2), delimiter=',')

timesa = []
timesb = []
Val25a = []
Val25b = []

row_countera= 0
for r in resultsa:
    row_countera += 1
    if row_countera>1:
        #Append each column in CSV to a separate list
        #this_time = dateutil.parser.parse(r[0])
        #this_time = this_time + datetime.timedelta(hours=30,minutes=43)
        #timesa.append(this_time) #converts str date and time to datetime
        timesa.append(dateutil.parser.parse(r[0]))
        Val25a.append(int(r[8]))

row_counterb= 0
for r in resultsb:
    row_counterb += 1
    if row_counterb>1:
        #Append each column in CSV to a separate list
        timesb.append(dateutil.parser.parse(r[0]))
        Val25b.append(int(r[8]))

n_merge = int(input("n data points to combine:"))
ndata_a = len(Val25a)
ndata_b = len(Val25b)
nsum_data_a= int(ndata_a/n_merge)
nsum_data_b= int(ndata_b/n_merge)

data_ave_a = []
data_ave_b = []
data_unc_a = []
data_unc_b = []
merge_times_a = []
merge_times_b = []

for i in range(nsum_data_a):
	idata = Val25a[i*n_merge:(i+1)*n_merge]
	idata_array = np.asarray(idata)
	aqmean = np.mean(idata_array)
	aqsigma = np.sqrt(np.var(idata_array))
	data_ave_a.append(aqmean)
	data_unc_a.append(aqsigma)
	itimes = timesa[i*n_merge:(i+1)*n_merge]
	itime = itimes[int(len(itimes)/2)]
	merge_times_a.append(itime)

for i in range(nsum_data_b):
	idata = Val25b[i*n_merge:(i+1)*n_merge]
	idata_array = np.asarray(idata)
	aqmean = np.mean(idata_array)
	aqsigma = np.sqrt(np.var(idata_array))
	data_ave_b.append(aqmean)
	data_unc_b.append(aqsigma)
	itimes = timesb[i*n_merge:(i+1)*n_merge]
	itime = itimes[int(len(itimes)/2)]
	merge_times_b.append(itime)

print("Touchpi Ave Data Length:", len(data_ave_a), "Openpi Ave Data Length:", len(data_ave_b))

fig = plt.figure()

plt.figure(1)
plt.plot(merge_times_a, data_ave_a, "b.", label='File 1')
plt.plot(merge_times_b, data_ave_b, "g.", label = 'File 2')
plt.legend(loc="best")
plt.xlabel("Time")
plt.ylabel("Particle Concentration 2.5")
file_title = "Air Quality Test Results"
plt.title(file_title)
fig.autofmt_xdate()

data_arrayA = np.asarray(data_ave_a)
data_arrayB = np.asarray(data_ave_b)
index = [0, len(data_arrayB) - 1, len(data_arrayB - 2), len(data_arrayB) - 3, len(data_arrayB) - 4]
data_arrayB = np.delete(data_arrayB, index)

corr_coeff = correlation_coefficient(data_arrayA, data_arrayB)
corr_statemnt = ('Correlation coefficient = ', corr_coeff)

plt.figure(2)
plt.plot(data_arrayA, data_arrayB, "b.")
plt.xlabel("Touchpi")
plt.ylabel("Openpi")
file_title2 = "AQ Sensor Correlation"
plt.title(file_title2)

print(corr_statemnt)

plt.show()




