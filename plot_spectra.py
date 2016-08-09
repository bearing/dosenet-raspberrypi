from collections import deque
import ast
from globalvalues import DEFAULT_DATALOG_D3S
import numpy as np
import os
import matplotlib.pyplot as plt

queue = deque('')

def grab_data(path=DEFAULT_DATALOG_D3S):
    """
    Takes data from datalog and places it in a queue
    """
    if os.path.isfile(path):
        with open(path, 'r') as f:
            data = f.read()
        data = ast.literal_eval(data)
        for i in data:
            queue.append(np.array(i))
def sum_data(data):
   """
   Sums up the data in the queue
   """
   total = data.popleft()
   i = 1
   while i < len(data):
       total += data.popleft()
       i+=1
   return total

def plot_data(data):
    """
    Plots data
    """
    plt.xlabel('Channel')
    plt.ylabel('Counts')
    x = np.linspace(0, len(data), len(data))
    plt.plot(x, data)
    plt.show()

def rebin(data, n=8):
    a = len(data)/n
    new_data = np.zeros((a, 1))
    i = 0 
    count = 0
    while i < a:
        temp = data[i:n]
        temp = sum(temp)
        new_data[count] = temp
        temp = []
        count+=1
        i+=n
        print new_data
    return new_data

def main(path=DEFAULT_DATALOG_D3S):
    if os.path.isfile(path):
        grab_data()
        total = sum_data(queue)
        test = rebin(total) 
        plot_data(test)
    else:
        print 'Datalog does not exist. Please run manager-D3S.py with datalog enabled.'

if __name__ == '__main__':      
    main()




