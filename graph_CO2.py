
import matplotlib.pyplot as plt
import csv
import dateutil
import time
import datetime
from matplotlib.dates import DateFormatter
import numpy as np

user_file = input("File Name: ")

results = csv.reader(open(user_file), delimiter=',')
times = []
CO2 = []
row_counter = 0
for r in results:
	row_counter += 1
	if row_counter>1:
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

fig = plt.figure()
ax = fig.add_subplot(111)
plt.plot(merge_times, data_ave, "b.")
plt.errorbar(merge_times, data_ave, yerr = data_unc)
plt.xlabel("Time")
plt.ylabel("CO2 (ppm)")
fig.autofmt_xdate()
ax.xaxis.set_major_formatter(DateFormatter('%m-%d-%Y %H:%M:%S'))
ax.set_xlim([datetime.datetime(2017, 8, 2, 10, 00, 00), datetime.datetime(2017, 8, 3, 00, 00, 00)])
plt.show()		

