#Code by Jennifer Atkins
#Created Thursday July 27, 2017 10:14:44
#Python file that graphs the correlation between data types in one aq file

import matplotlib.pyplot as plt
import csv
import numpy as np
from scipy.stats.stats import pearsonr

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

user_file = input("File Name: ")
results = csv.reader(open(user_file), delimiter=',')

print("KEY: 1 = 0.3um, 2 = 0.5um, 3 = 1.0um, 4 = 2.5um, 5 = 5.0um, 6 = 10um, 7 = PM 1.0, 8 = PM 2.5, 9 = PM 10")

data_a = int(input("Particulate Size 1 (Enter a number between 1 and 9): "))
data_b = int(input("Particulate Size 2 (Enter a different number between 1 and 9): "))

labelA = []
labelB = []

if data_a == 1:
	labelA.append("0.3 um")
elif data_a == 2:
	labelA.append("0.5 um")
elif data_a == 3:
	labelA.append("1.0 um")
elif data_a == 4:
	labelA.append("2.5 um")
elif data_a == 5:
	labelA.append("5.0 um")
elif data_a == 6:
	labelA.append("10 um")
elif data_a == 7:
	labelA.append("PM 1.0")
elif data_a == 8:
	labelA.append("PM 2.5")
elif data_a == 9:
	labelA.append("PM 10")

if data_b == 1:
	labelB.append("0.3 um")
elif data_b == 2:
	labelB.append("0.5 um")
elif data_b == 3:
	labelB.append("1.0 um")
elif data_b == 4:
	labelB.append("2.5 um")
elif data_b == 5:
	labelB.append("5.0 um")
elif data_b == 6:
	labelB.append("10 um")
elif data_b == 7:
	labelB.append("PM 1.0")
elif data_b == 8:
	labelB.append("PM 2.5")
elif data_b == 9:
	labelB.append("PM 10")

Alabel = ''.join(labelA)
Blabel = ''.join(labelB)

ValA = []
ValB = []

row_counter= 0
for r in results:
    row_counter += 1
    if row_counter>1:
        #Append each column in CSV to a separate list
        ValA.append(int(r[data_a]))
        ValB.append(int(r[data_b]))

n_merge = int(input("n data points to combine:"))
ndata_a = len(ValA)
ndata_b = len(ValB)
nsum_data_a= int(ndata_a/n_merge)
nsum_data_b= int(ndata_b/n_merge)

data_ave_a = []
data_ave_b = []
data_unc_a = []
data_unc_b = []

for i in range(nsum_data_a):
	idata = ValA[i*n_merge:(i+1)*n_merge]
	idata_array = np.asarray(idata)
	aqmeana = np.mean(idata_array)
	aqsigmaA = np.sqrt(np.var(idata_array))
	data_ave_a.append(aqmeana)
	data_unc_a.append(aqsigmaA)

for i in range(nsum_data_b):
	idata = ValB[i*n_merge:(i+1)*n_merge]
	idata_array = np.asarray(idata)
	aqmeanb = np.mean(idata_array)
	aqsigmaB = np.sqrt(np.var(idata_array))
	data_ave_b.append(aqmeanb)
	data_unc_b.append(aqsigmaB)

correlation_values = pearsonr(data_ave_a, data_ave_b)
p_value = ("p Value =", correlation_values[1])

corr_coeff = correlation_coefficient(np.asarray(data_ave_a),np.asarray(data_ave_b))
corr_statemnt = "Correlation coefficient = ", corr_coeff

plt.figure(1)
plt.plot(data_ave_a, data_ave_b, "b.")
plt.xlabel(Alabel)
plt.ylabel(Blabel)
file_title = "Air Quality Correlation Results"
plt.annotate(corr_statemnt, xy=(0, 1), xytext=(12, -12), va='top',
	xycoords='axes fraction', textcoords='offset points')
plt.annotate(p_value, xy=(0, .94), xytext=(12, -12), va='top',
	xycoords='axes fraction', textcoords='offset points')
plt.title(file_title)

plt.show()




