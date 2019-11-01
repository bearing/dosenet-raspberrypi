import csv
import datetime
import matplotlib.pyplot as plt

filename = raw_input('Please enter the directory of the filename: ')

with open(filename) as csvfile:
    file = csv.reader(csvfile, delimiter=',')
    
    x = []
    y = []
    yerr = []
    
    for row in file:
        
        print(row)
        try:
            x.append(float(row[0]))
            y.append(float(row[1]))
            yerr.append(float(row[2]))
        except Exception as e:
            print(e)
            pass
    plt.plot(x, y)
    plt.errorbar(x, y, yerr)
    
    plt.xlabel('time')
    plt.ylabel('ppm')
    
    plt.title(filename)
    
    plt.show()
 
'''   
    for row in file:
        print(row[0])
        time = dt.datetime(row[0])
        ppm = row[1]
        unc. = row[2]
        
        py.plot
'''
    
