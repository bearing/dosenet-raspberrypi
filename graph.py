# Python file to graph air quality test results
import matplotlib.pyplot as plt
import csv
from dateutil import parser


results = csv.reader(open("air_quality_test_results.csv"), delimiter=',')
times = []
P3 = []
P5 = []
P10 = []
P25 = []
P50 = []
P100 = []

row_counter= 0
for r in results:
    row_counter += 1
    if row_counter>1:
        #Append each column in CSV to a separate list
        times.append(parser.parse(r[0])) #converts str date and time to datetime
        P3.append(r[1])
        P5.append(r[2])
        P10.append(r[3])
        P25.append(r[4])
        P50.append(r[5])
        P100.append(r[6])

#Use plot() method to graph
plt.plot(times, P3, "b")
plt.plot(times, P5, "g")
plt.plot(times, P10, "r")
plt.plot(times, P25, "m")
plt.plot(times, P50, "orange")
plt.plot(times, P100, "purple")
