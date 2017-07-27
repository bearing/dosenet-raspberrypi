
import matplotlib.pyplot as plt
from matplotlib import style
import csv
import dateutil
import time
import datetime
import numpy as np

user_file = input("File Name 1: ")

results = csv.reader(open(user_file), delimiter=',')
times = []
CO2 = []
row_counter = 0
for r in results:
	row_counter += 1
	if row_counter>1:
		#this_time = dateutil.parser.parse(r[0])
		#this_time = this_time + datetime.timedelta(hours=30,minutes=43)
		times.append(dateutil.parser.parse(r[0]))
		CO2.append(int(r[1]))

n_merge = int(input("n data points to combine:"))
ndata = len(CO2)
nsum_data = int(ndata/n_merge)

data_ave = []
data_unc = []
merge_times = []

for i in range(nsum_data):
	idata = CO2[i*n_merge:(i+1)*n_merge]
	idata_array = np.asarray(idata)
	CO2mean = np.mean(idata_array)
	CO2sigma = np.sqrt(np.var(idata_array))
	data_ave.append(CO2mean)
	data_unc.append(CO2sigma)
	itimes = times[i*n_merge:(i+1)*n_merge]
	itime = itimes[int(len(itimes)/2)]
	merge_times.append(itime)

user_file_2 = input("File Name 2: ")

results_2 = csv.reader(open(user_file_2), delimiter=',')
times_2 = []
CO2_2 = []
row_counter = 0
for r in results_2:
	row_counter += 1
	if row_counter>1:
		times_2.append(dateutil.parser.parse(r[0]))
		CO2_2.append(int(r[1]))

n_merge_2 = int(input("n data points to combine:"))
ndata_2 = len(CO2_2)
nsum_data_2 = int(ndata_2/n_merge_2)

data_ave_2 = []
data_unc_2 = []
merge_times_2 = []

for i in range(nsum_data_2):
	idata_2 = CO2_2[i*n_merge_2:(i+1)*n_merge_2]
	idata_array_2 = np.asarray(idata_2)
	CO2mean_2 = np.mean(idata_array_2)
	CO2sigma_2 = np.sqrt(np.var(idata_array_2))
	data_ave_2.append(CO2mean_2)
	data_unc_2.append(CO2sigma_2)
	itimes_2 = times_2[i*n_merge_2:(i+1)*n_merge_2]
	itime_2 = itimes_2[int(len(itimes_2)/2)]
	merge_times_2.append(itime_2)	

fig = plt.figure()
plt.plot(merge_times, data_ave, "b.", label="File 1")
plt.plot(merge_times_2, data_ave_2, "g.", label="File 2")
plt.errorbar(merge_times, data_ave, yerr = data_unc)
plt.errorbar(merge_times_2, data_ave_2, yerr = data_unc_2)
plt.xlabel("Time")
plt.ylabel("CO2 (ppm)")
plt.legend()
plt.grid(True,color='k')
fig.autofmt_xdate()
plt.show()		
