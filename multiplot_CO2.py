
import matplotlib.pyplot as plt
from matplotlib import style
import csv
import dateutil
import time
import datetime
import numpy as np
from scipy.stats.stats import pearsonr

def get_covariance(yfile1, yfile2):
	yfile1_sigma = np.sqrt(np.var(yfile1))
	yfile2_sigma = np.sqrt(np.var(yfile2))
	yfile1_mean = np.mean(yfile1)
	yfile2_mean = np.mean(yfile2)

	files1and2_sum = 0
	for i in range(len(yfile1)):
		files1and2_sum = files1and2_sum + (yfile1[i]-yfile1_mean)*(yfile2[i]-yfile2_mean)
	correlation_coef = files1and2_sum / ((yfile1_sigma)*(yfile2_sigma)) / len(yfile1)
	return correlation_coef

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

CO2file1_array = np.asarray(data_ave)
CO2file2_array = np.asarray(data_ave_2)
correlation_coef = get_covariance(CO2file1_array, CO2file2_array)
print("Correlation: {}".format(correlation_coef))

print("Length of touch data: {}, Length of open data: {}".format(len(data_ave),len(data_ave_2)))

#index = [len(CO2file2_array) - 1, len(CO2file2_array) - 2, len(CO2file2_array) - 3, len(CO2file2_array) - 4, len(CO2file2_array) - 5]
#CO2file2_array	 = np.delete(CO2file2_array, index)

correlation_values = pearsonr(CO2file1_array, CO2file2_array)
print("p value =", correlation_values[1])

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
x.xaxis.set_major_formatter(DateFormatter('%d-%m-%y %H:%M:%S'))
ax.set_xlim([datetime.datetime(2017, 8, 2, 10, 00, 00), datetime.datetime(2017, 8, 3, 00, 00, 00)])
fig = plt.figure()
plt.plot(CO2file1_array, CO2file2_array, "b.")
plt.xlabel("CO2 file 1")
plt.ylabel("CO2 file 2")

corr_statement = "Correlation Coefficient =", correlation_coef
p_value = "P Value =", correlation_values[1]
plt.annotate(corr_statement, xy=(0,1), xytext=(12,-12), va='top',
	xycoords='axes fraction', textcoords='offset points')
plt.annotate(p_value, xy=(0,0.94), xytext=(12,-12), va='top',
	xycoords='axes fraction', textcoords='offset points')
plt.show()		
