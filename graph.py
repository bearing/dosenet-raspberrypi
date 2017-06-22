# Python file to graph air quality test results
import matplotlib
import csv
from dateutil import parser

results = csv.reader('air_quality_test_results.csv', delimiter=',')

times = []
P3 = []
P5 = []
P10 = []
P25 = []
P50 = []
p100 = []

row_counter= 0
for r in results:
    row_counter += 1
    if row_counter>0:
        #Append each column in CSV to a separate list
        times.append(parser.parse(r[0])) #converts str date and time to datetime
        P3.append(r[1])
        P5.append(r[2])
        P10.append(r[3])
        P25.append(r[4])
        P50.append(r[5])
        P100.append(r[6])

        #Use plot() method to graph
        matplotlib.pyplot.plot(times[r], P3[r], "b")
        matplotlib.pyplot.plot(times[r], P5[r], "g")
        matplotlib.pyplot.plot(times[r], P10[r], "r")
        matplotlib.pyplot.plot(times[r], P25[r], "m")
        matplotlib.pyplot.plot(times[r], P50[r], "orange")
        matplotlib.pyplot.plot(times[r], P100[r], "purple")

        
