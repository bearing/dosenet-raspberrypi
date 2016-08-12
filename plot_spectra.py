from collections import deque
import ast
from globalvalues import DEFAULT_DATALOG_D3S
import numpy as np
import os
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import axes3d
from matplotlib.collections import PolyCollection
from matplotlib.colors import colorConverter

queue = deque('')

def grab_data(path=DEFAULT_DATALOG_D3S):
    """
    Takes data from datalog and places it in a queue. Rebin data here.
    """
    if os.path.isfile(path):
        with open(path, 'r') as f:
            data = f.read()
        data = ast.literal_eval(data)
        for i in data:
            new_data = rebin(np.array(i))
            queue.append(new_data)

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
    x = np.linspace(0, 4096, 256)
    plt.plot(x, data, drawstyle='steps-mid')
    plt.show()

def rebin(data, n=4):
    """
    Rebins the array. n is the divisor. Rebin the data in the grab_data method. 
    """
    a = len(data)/n
    new_data = np.zeros((256, 1))
    i = 0 
    count = 0
    while i < a:
        temp = sum(data[i:n*(count+1)])
        new_data[count] = temp
        count+=1
        i+=n
    return new_data

def cc(arg):
    """
    Converts string to colors
    """
    return colorConverter.to_rgba(arg, alpha=0.6)
    
def generate_colors(length):
    """
    Generates a list of colors for the waterfall graph
    """
    lst = []
    color = 'r'
    i = 0 
    while i < length: 
        lst.append(cc(color))
        if color == 'r':
            color = 'g'
        elif color == 'g':
            color = 'b'
        elif color == 'b':
            color = 'y'
        else:
            color = 'r'
        i+=1
    return lst

def sum_graph(path=DEFAULT_DATALOG_D3S):
    """
    Plots the sum of all the spectra
    """
    if os.path.isfile(path):
        grab_data()
        total = sum_data(queue)
        plot_data(total)
        
    else:
        print 'Datalog does not exist. Please run manager-D3S.py with datalog enabled.'
        
def waterfall_graph(path=DEFAULT_DATALOG_D3S):
    """
    Plots a waterfall graph of all the spectra. Could clean up a bit. Could also use a more general way to determine the count axis
    """
    if os.path.isfile(path):
        grab_data()
        length = len(queue)
        color = generate_colors(length)
        
        plt.imshow(queue[0])
        plt.show

        y = np.linspace(0, 4096, 256)
        x = np.linspace(0, length-1, length)
        fig = plt.figure()
        ax = fig.gca(projection='3d')
        verts = []
        i = 0 
        while i < length:
            verts.append(list(zip(y, queue[i])))
            i+=1
            
        
        poly = PolyCollection(verts, facecolors=color)
        poly.set_alpha(0.7)
        ax.add_collection3d(poly, zs = x, zdir='y')
        
        ax.set_xlabel('Channel')
        ax.set_xlim3d(0, 4096)
        ax.set_ylabel('Time')
        ax.set_ylim3d(0, length - 1)
        ax.set_zlabel('Counts')
        ax.set_zlim3d(0, 50)
            
        plt.show()
    else:
        print 'Datalog does not exist. Please run manager-D3S.py with datalog enabled.'

if __name__ == '__main__':      
    sum_graph()
    waterfall_graph()
