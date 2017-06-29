
import matplotlib.pyplot as plt
import csv
import dateutil
import time
import datetime

user_file = input("What CO2 concentration test result file do you want to graph? (Put quotation marks around the file name.) File Name: ")

results = csv.reader(open(user_file), delimiter=',')
times = []
CO2 = []
row_counter = 0
for r in results:
	row_counter += 1
	if row_counter>1:
		times.append(dateutil.parser.parse(r[0]))
		CO2.append(int(r[1]))

plt.plot(times, CO2, "b.")
plt.xlabel("Time")
plt.ylabel("CO2 (ppm)")
plt.show()		
