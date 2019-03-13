import csv
import datetime

with open('filename') as csvfile:
    file = csv.reader(csvfile, delimiter=',')
    for row in file:
        print(row[0])
        time = dt.datetime(row[0])
    
