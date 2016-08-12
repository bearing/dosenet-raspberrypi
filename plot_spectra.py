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

def main(path=DEFAULT_DATALOG_D3S):
    if os.path.isfile(path):
        grab_data()
        total = sum_data(queue)
        plot_data(total)
        
    else:
        print 'Datalog does not exist. Please run manager-D3S.py with datalog enabled.'
        
def main_2(path=DEFAULT_DATALOG_D3S):
    if os.path.isfile(path):
        grab_data()
        length = len(queue)
        y = np.linspace(0, 4096, 256)
        x = np.linspace(0, length-1, length)
        fig = plt.figure()
        ax = fig.gca(projection='3d')
        def cc(arg):
            return colorConverter.to_rgba(arg, alpha=0.6)
        verts = []
        i = 0 
        while i < length:
            verts.append(list(zip(y, queue[i])))
            i+=1
            
        
        poly = PolyCollection(verts, facecolors=[cc('b'), cc('g'), cc('b'),
                                                 cc('r'), cc('b')])
        poly.set_alpha(0.7)
        ax.add_collection3d(poly, zs = x, zdir='y')
        
        ax.set_xlabel('X')
        ax.set_xlim3d(0, 4096)
        ax.set_ylabel('Y')
        ax.set_ylim3d(0, length - 1)
        ax.set_zlabel('Z')
        ax.set_zlim3d(0, 50)
            
        plt.show()
    else:
        print 'Datalog does not exist. Please run manager-D3S.py with datalog enabled.'

if __name__ == '__main__':      
    main()
    main_2()
