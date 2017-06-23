# Python file to graph air quality test results
import matplotlib.pyplot as plt
import csv
from dateutil import parser
import argparse
import numpy
import time
import datetime

user_file = input("What air quality test result file do you want to graph? (Put quotes around the file name) Name: ")
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
    print(r)
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

new_P3 = []
new_P5 = []
new_P10 = []
new_P25 = []
new_P50 = []
new_P100 = []

#Get rid of unnecessary data
remainder_P3 = 0-(len(P3)%(combine_number))
if remainder_P3 !=0:
    P3.pop(remainder_P3)

remainder_P5 = 0-(len(P5)%(combine_number))
if remainder_P5 !=0:
    P5.pop(remainder_P5)

remainder_P10 = 0-(len(P10)%(combine_number))
if remainder_P10 !=0:
    P10.pop(remainder_P10)

remainder_P25 = 0-(len(P25)%(combine_number))
if remainder_P25 !=0:
    P25.pop(remainder_P25)

remainder_P50 = 0-(len(P50)%(combine_number))
if remainder_P50 !=0:
    P50.pop(remainder_P50)

remainder_P100 = 0-(len(P100)%(combine_number))
if remainder_P100 !=0:
    P100.pop(remainder_P100)

#Add up data
for i in range((len(P3)/combine_number)-1):
    numberA = (i*combine_number) + 1
    numberB = (i*combine_number) + combine_number
    sum_P3 = [sum(P3[numberA:numberB])]
    new_P3.append(sum_P3)

for i in range((len(P5)/combine_number)-1):
    numberC = (i*combine_number) + 1
    numberD = (i*combine_number) + combine_number
    sum_P5 = [sum(P5[numberC:numberD])]
    new_P5.append(sum_P5)

for i in range((len(P10)/combine_number)-1):
    numberE = (i*combine_number) + 1
    numberF = (i*combine_number) + combine_number
    sum_P10 = [sum(P10[numberE:numberF])]
    new_P10.append(sum_P10)

for i in range((len(P25)/combine_number)-1):
    numberG = (i*combine_number) + 1
    numberH = (i*combine_number) + combine_number
    sum_P25 = [sum(P25[numberG:numberH])]
    new_P25.append(sum_P25)

for i in range((len(P50)/combine_number)-1):
    numberJ = (i*combine_number) + 1
    numberK = (i*combine_number) + combine_number
    sum_P50 = [sum(P50[numberJ:numberK])]
    new_P50.append(sum_P50)

for i in range((len(P100)/combine_number)-1):
    numberL = (i*combine_number) + 1
    numberM = (i*combine_number) + combine_number
    sum_P100 = [sum(P100[numberL:numberM])]
    new_P100.append(sum_P100)

#Get rid of last time if unecessary
if remainder_P25 !=0:
    times.pop(-1:remainder_P25)

#Convert time into epoch seconds
seconds_times = [timedelta.total_seconds(t) for t in times]

#Find middle time
time = numpy.where(numpy.array(seconds_times))
if len(time[0])%2 == 0: #if length of list is even
    middle_item1 = len(time[0])/2
    middle_item2 = middle_item1 + 1
    middletime_sec = (time[0][middle_item1] + time[0][middle_item2])/2

else: #if length of list is odd
    middle_item = len(time[0])/2 + 1
    middletime_sec = time[0][middle_item]

#Convert epoch seconds back into h:m:s
middletime = datetime.strptime(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(middletime_sec)))

#Use plot() method to graph
plt.plot(middletime, new_P3, "b.")
plt.plot(middletime, new_P5, "g.")
plt.plot(middletime, new_P10, "r.")
plt.plot(middletime, new_P25, "m.")
plt.plot(middletime, new_P50, "y.")
plt.plot(middletime, new_P100, "c.")
plt.show()
