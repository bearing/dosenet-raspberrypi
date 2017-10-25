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

times_array = np.asarray(times)

print('Only input "0" to Start Time if you want the whole graph')
intial_srtT = input('Start Time (month date year hour minute second):')

if intial_srtT == '0':
	subtime_array = times
	data_array = CO2
else:
	intial_stpT = input('Stop Time (month date year hour minute second):')
	
	srtT = intial_srtT.split()
	stpT = intial_stpT.split()

	srty = int(srtT[2])
	srtm = int(srtT[0])
	srtd = int(srtT[1])
	srtH = int(srtT[3])
	srtM = int(srtT[4])
	srtS = int(srtT[5])

	stpy = int(stpT[2])
	stpm = int(stpT[0])
	stpd = int(stpT[1])
	stpH = int(stpT[3])
	stpM = int(stpT[4])
	stpS = int(stpT[5])

	start = datetime.datetime(srty, srtm, srtd, srtH, srtM, srtS)
	stop = datetime.datetime(stpy, stpm, stpd, stpH, stpM, stpS)

	wheretime_array = np.where((times_array>=start)&(times_array<=stop) ) 
	subtime_array = times_array[wheretime_array]

	bgndffrnce_array = np.where(times_array<start)
	subbgndffrnce_array = times_array[bgndffrnce_array]

	enddffrnce_array = np.where(times_array>stop)
	subenddffrnce_array = times_array[enddffrnce_array]

	for i in range(0,len(bgndffrnce_array)):
	    CO2.pop( )

	for i in range(len(subtime_array),len(CO2)):
	    CO2.pop( )
	data_array = np.asarray(CO2)

n_merge = int(input("n data points to combine:"))
ndata = len(data_array)
nsum_data = int(ndata/n_merge)

data_ave = []
data_unc = []
merge_times = []

for i in range(nsum_data):
	idata = data_array[i*n_merge:(i+1)*n_merge]
	idata_array = np.asarray(idata)
	CO2mean = np.mean(idata_array)
	CO2sigma = np.sqrt(np.var(idata_array))
	data_ave.append(CO2mean)
	data_unc.append(CO2sigma)
	itimes = subtime_array[i*n_merge:(i+1)*n_merge]
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
plt.show()		