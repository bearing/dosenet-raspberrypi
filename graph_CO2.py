
import matplotlib.pyplot as plt
import csv
import dateutil
import time
import datetime

user_file = datetime.datetime.strftime("%Y-%m-%d %H:%M:%S")
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
plt.show()		
