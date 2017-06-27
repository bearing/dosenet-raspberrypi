# Python file that graphs air quality test result CSV files

import matplotlib.pyplot as plt
import csv
import dateutil
import argparse
import numpy
import time
import datetime

user_file = input("What air quality test result file do you want to graph? (Put quotes around the file name.) File Name: ")
results = csv.reader(open(user_file), delimiter=',')

#Given a certain argument, combine results for each size molecule
parser = argparse.ArgumentParser()
parser.add_argument("combinenumber", type = float)
info = parser.parse_args()
combine_number = info.combinenumber

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
        times.append(dateutil.parser.parse(r[0])) #converts str date and time to datetime
        P3.append(r[1])
        P5.append(r[2])
        P10.append(r[3])
        P25.append(r[4])
        P50.append(r[5])
        P100.append(r[6])

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

new_P3 = []
new_P5 = []
new_P10 = []
new_P25 = []
new_P50 = []
new_P100 = []

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

#Add up data
for i in range(int(len(P3)/combine_number)):
    numberA = int((i*combine_number) + 1)
    numberB = int((i*combine_number) + combine_number)
    sum_P3 = [sum(P3[numberA:numberB])]
    new_P3.append(sum_P3)

for i in range(int(len(P5)/combine_number)):
    numberC = int((i*combine_number) + 1)
    numberD = int((i*combine_number) + combine_number)
    sum_P5 = [sum(P5[numberC:numberD])]
    new_P5.append(sum_P5)

for i in range(int(len(P10)/combine_number)):
    numberE = int((i*combine_number) + 1)
    numberF = int((i*combine_number) + combine_number)
    sum_P10 = [sum(P10[numberE:numberF])]
    new_P10.append(sum_P10)

for i in range(int(len(P25)/combine_number)):
    numberG = int((i*combine_number) + 1)
    numberH = int((i*combine_number) + combine_number)
    sum_P25 = [sum(P25[numberG:numberH])]
    new_P25.append(sum_P25)

for i in range(int(len(P50)/combine_number)):
    numberJ = int((i*combine_number) + 1)
    numberK = int((i*combine_number) + combine_number)
    sum_P50 = [sum(P50[numberJ:numberK])]
    new_P50.append(sum_P50)

for i in range(int(len(P100)/combine_number)):
    numberL = int((i*combine_number) + 1)
    numberM = int((i*combine_number) + combine_number)
    sum_P100 = [sum(P100[numberL:numberM])]
    new_P100.append(sum_P100)

#Get rid of last time if unecessary
if remainder_P25 !=0:
    for i in range(int(remainder_P25)):
        times.pop()

#State how many results have been excluded
if int(remainder_P25) != 1:
    print(str(int(remainder_P25))+" results have been excluded from the graph.")

else:
    print("1 result has been excluded from the graph.")

#Convert time into epoch seconds
seconds_times = [time.mktime(t.timetuple()) for t in times]

#Find middle time
middletimes = []
for i in range(int(len(seconds_times)/combine_number)):
    numberN = int((i*combine_number) + 1)
    numberP = int((i*combine_number) + combine_number)
    time = numpy.array(seconds_times[numberN:numberP])
    timelength = numpy.where(time)

    #if length of list is even
    if len(timelength[0])%2 == 0:
        middle_item1 = len(timelength[0])/2
        middle_item2 = middle_item1 - 1
        middletime_sec = (time[middle_item1] + time[middle_item2])/2
        middletimes.append(middletime_sec)

    #if length of list is odd
    elif len(timelength[0])%2 != 0:
        middle_item = int(len(timelength[0])/2)
        middletime_sec = time[middle_item]
        middletimes.append(middletime_sec)

#Convert epoch seconds back into h:m:s
middletime_final = []
for i in range(len(middletimes)):
    t = datetime.datetime.utcfromtimestamp(middletimes[i]/1000)
    from_zone = dateutil.tz.tzutc()
    to_zone = dateutil.tz.tzlocal()
    t = t.replace(tzinfo=from_zone)
    loc_zone = t.astimezone(to_zone)
    middletime_final.append(loc_zone)

#Use plot() method to graph
plt.plot(middletime_final, new_P3, "b.")
plt.plot(middletime_final, new_P5, "g.")
plt.plot(middletime_final, new_P10, "r.")
plt.plot(middletime_final, new_P25, "m.")
plt.plot(middletime_final, new_P50, "y.")
plt.plot(middletime_final, new_P100, "c.")
plt.show()
