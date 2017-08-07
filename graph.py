# Python file that graphs air quality test result CSV files

import matplotlib.pyplot as plt
import matplotlib.figure as fig
import matplotlib.pylab as pyl
import matplotlib
import csv
import dateutil
import argparse
import numpy
import time
import datetime
from matplotlib.dates import DateFormatter

#Given a certain argument, combine results for each size molecule
parser = argparse.ArgumentParser()
parser.add_argument("combinenumber", type = int, help = "Enter a natural number value that will determine the amount of results added together before being graphed")
info = parser.parse_args()
combine_number = info.combinenumber

user_file = input("What air quality test result file do you want to graph? (Put quotation marks around the file name.) File Name: ")
results = csv.reader(open(user_file), delimiter=',')

times = []
P3 = []
P5 = []
P10 = []
P25 = []
P50 = []
P100 = []
Val10 = []
Val25 = []
Val100 = []

row_counter= 0
for r in results:
    row_counter += 1
    if row_counter>1:
        #Append each column in CSV to a separate list
        times.append(dateutil.parser.parse(r[0])) #converts str date and time to datetime
        P3.append(r[1])
        P5.append(r[2])
        P10.append(r[3])
        P25.append(r[4])
        P50.append(r[5])
        P100.append(r[6])
        Val10.append(r[7])
        Val25.append(r[8])
        Val100.append(r[9])

#Make sure the argument was valid
while len(times)< combine_number or combine_number<1:
    if len(times) == 1:
        print("The number provided was too large or not a natural number. There is only 1 result. All data points will be graphed.")
        combine_number = 1

    elif len(times) == 0:
        print("There are no results in the document provided.")
        quit()

    else:
        combine_number = input("The number provided was too large or not a natural number. There are "+str(len(times))+" results. Choose a natural number between 1 and "+str(len(times))+" that will determine the amount of results added together before being graphed. Number: ")

#convert str into int
for i in range(len(P3)):
    P3[i] = int(P3[i])

for i in range(len(P5)):
    P5[i] = int(P5[i])

for i in range(len(P10)):
    P10[i] = int(P10[i])

for i in range(len(P25)):
    P25[i] = int(P25[i])

for i in range(len(P50)):
    P50[i] = int(P50[i])

for i in range(len(P100)):
    P100[i] = int(P100[i])

for i in range(len(Val10)):
    Val10[i] = int(Val10[i])

for i in range(len(Val25)):
    Val25[i] = int(Val25[i])

for i in range(len(Val100)):
    Val100[i] = int(Val100[i])

new_P3 = []
new_P5 = []
new_P10 = []
new_P25 = []
new_P50 = []
new_P100 = []
new_Val10 = []
new_Val25 = []
new_Val100 = []

#Get rid of unnecessary data
remainder_P3 = (len(P3)%(combine_number))
if remainder_P3 !=0:
    for i in range(int(remainder_P3)):
        P3.pop()

remainder_P5 = (len(P5)%(combine_number))
if remainder_P5 !=0:
    for i in range(int(remainder_P5)):
        P5.pop()

remainder_P10 = (len(P10)%(combine_number))
if remainder_P10 !=0:
    for i in range(int(remainder_P10)):
        P10.pop()

remainder_P25 = (len(P25)%(combine_number))
if remainder_P25 !=0:
    for i in range(int(remainder_P25)):
        P25.pop()

remainder_P50 = (len(P50)%(combine_number))
if remainder_P50 !=0:
    for i in range(int(remainder_P50)):
        P50.pop()

remainder_P100 = (len(P100)%(combine_number))
if remainder_P100 !=0:
    for i in range(int(remainder_P100)):
        P100.pop()

remainder_Val10 = (len(Val10)%(combine_number))
if remainder_Val10 !=0:
    for i in range(int(remainder_Val10)):
        Val10.pop()

remainder_Val25 = (len(Val25)%(combine_number))
if remainder_Val25 !=0:
    for i in range(int(remainder_Val25)):
        Val25.pop()

remainder_Val100 = (len(Val100)%(combine_number))
if remainder_Val100 !=0:
    for i in range(int(remainder_Val100)):
        Val100.pop()

#Add up data
for i in range(int(len(P3)/combine_number)):
    numberA = int(i*combine_number)
    numberB = int((i*combine_number) + combine_number)
    sum_P3 = [sum(P3[numberA:numberB])]
    new_P3.append(sum_P3)

for i in range(int(len(P5)/combine_number)):
    numberC = int(i*combine_number)
    numberD = int((i*combine_number) + combine_number)
    sum_P5 = [sum(P5[numberC:numberD])]
    new_P5.append(sum_P5)

for i in range(int(len(P10)/combine_number)):
    numberE = int(i*combine_number)
    numberF = int((i*combine_number) + combine_number)
    sum_P10 = [sum(P10[numberE:numberF])]
    new_P10.append(sum_P10)

for i in range(int(len(P25)/combine_number)):
    numberG = int(i*combine_number)
    numberH = int((i*combine_number) + combine_number)
    sum_P25 = [sum(P25[numberG:numberH])]
    new_P25.append(sum_P25)

for i in range(int(len(P50)/combine_number)):
    numberJ = int(i*combine_number)
    numberK = int((i*combine_number) + combine_number)
    sum_P50 = [sum(P50[numberJ:numberK])]
    new_P50.append(sum_P50)

for i in range(int(len(P100)/combine_number)):
    numberL = int((i*combine_number) + 1)
    numberM = int((i*combine_number) + combine_number)
    sum_P100 = [sum(P100[numberL:numberM])]
    new_P100.append(sum_P100)

for i in range(int(len(Val10)/combine_number)):
    numberQ = int(i*combine_number)
    numberR = int((i*combine_number) + combine_number)
    sum_Val10 = [sum(Val10[numberQ:numberR])]
    new_Val10.append(sum_Val10)

for i in range(int(len(Val25)/combine_number)):
    numberS = int(i*combine_number)
    numberT = int((i*combine_number) + combine_number)
    sum_Val25 = [sum(Val25[numberS:numberT])]
    new_Val25.append(sum_Val25)

for i in range(int(len(Val100)/combine_number)):
    numberV = int(i*combine_number)
    numberW = int((i*combine_number) + combine_number)
    sum_Val100 = [sum(Val100[numberV:numberW])]
    new_Val100.append(sum_Val100)

#State how many results have been excluded
if int(remainder_P25) != 1:
    print(str(int(remainder_P25))+" results have been excluded from the graph.")

else:
    print("1 result has been excluded from the graph.")

#Find middle time
middletimes = []
for i in range(int(len(times)/combine_number)):
    numberN = int(i*combine_number)
    numberP = int((i*combine_number) + combine_number)
    time = times[numberN:numberP]

    middletimes.append(time[int(len(time)/2)])

print(middletimes)
#Use plot() method to graph particle count vs. time and add legend
fig = plt.figure()

plt.figure(1)
ax = fig.add_subplot(111)
plt.plot(middletimes, new_P3, "b.", label='P3')
plt.plot(middletimes, new_P5, "g.", label = 'P5')
plt.plot(middletimes, new_P10, "r.", label = 'P10')
plt.plot(middletimes, new_P25, "m.", label = 'P25')
plt.plot(middletimes, new_P50, "y.", label = 'P50')
plt.plot(middletimes, new_P100, "c.", label = 'P100')
plt.legend(loc="best")
plt.xlabel("Time")
plt.ylabel("Particle Count")
file_title = "Air Quality Test Results: From "+datetime.datetime.strftime(times[0], "%Y-%m-%d %H:%M:%S")+" To "+datetime.datetime.strftime(times[-1], "%Y-%m-%d %H:%M:%S")
plt.title(file_title)
fig.autofmt_xdate()
ax.xaxis.set_major_formatter(DateFormatter('%m-%d-%Y %H:%M:%S'))

#Use plot() method to graph particle concentration vs. time and add legend
fig = plt.figure()

plt.figure(2)
ax = fig.add_subplot(111)
plt.plot(middletimes, new_Val10, "b.", label='1.0')
plt.plot(middletimes, new_Val25, "g.", label = '2.5')
plt.plot(middletimes, new_Val100, "r.", label = '10')
plt.legend(loc="best")
plt.xlabel("Time")
plt.ylabel("Particle Concentration")
file_title = "Air Quality Test Results: From "+datetime.datetime.strftime(times[0], "%Y-%m-%d %H:%M:%S")+" To "+datetime.datetime.strftime(times[-1], "%Y-%m-%d %H:%M:%S")
plt.title(file_title)
fig.autofmt_xdate()
ax.xaxis.set_major_formatter(DateFormatter('%m-%d-%Y %H:%M:%S'))
ax.set_xlim([datetime.datetime(2017, 8, 2, 10, 00, 00), datetime.datetime(2017, 8, 3, 00, 00, 00)])
plt.show()
