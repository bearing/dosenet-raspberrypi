from __future__ import print_function
from collections import deque
import ast
from globalvalues import DEFAULT_DATALOG_D3S
import numpy as np
import os
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import axes3d
from matplotlib.collections import PolyCollection
from matplotlib.colors import colorConverter


def decide_path():
    path = raw_input('What is the path? Type None for DEFAULT_DATALOG_D3S. ' +
                     'Do not use quotes.\n')
    return path


def grab_data(path):
    """
    Takes data from datalog and places it in a queue. Rebin data here.
    """
    if os.path.isfile(path):
        with open(path, 'r') as f:
            data = f.read()
        data = ast.literal_eval(data)
        queue = deque('')
        for i in data:
            new_data = rebin(np.array(i))
            queue.append(new_data)
        return queue


def sum_data(data):
    """
    Sums up the data in the queue
    """
    total = data.popleft()
    i = 1
    while i < len(data):
        total += data.popleft()
        i += 1
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
        count += 1
        i += n
    return new_data


def make_image(queue):
    """
    Prepares an array for the waterfall plot
    """
    length = len(queue)

    image = np.zeros((length, 256))
    i = 0
    while i < length:
        image[i] = fix_array(queue.popleft())
        i += 1
    return image


def fix_array(array):
    """
    Used to format arrays for the waterfall plot.
    """
    new_array = np.zeros((256))
    i = 0
    while i < 256:
        new_array[i] = array[i]
        i += 1
    return new_array


def sum_graph(path):
    """
    Plots the sum of all the spectra
    """
    if os.path.isfile(path):
        queue = grab_data(path)
        total = sum_data(queue)
        plot_data(total)

    else:
        print('Datalog does not exist. ' +
              'Please run manager-D3S.py with datalog enabled.')


def waterfall_graph(path):
    """
    Plots a waterfall graph of all the spectra.
    """
    if os.path.isfile(path):
        queue = grab_data(path)
        queue_length = len(queue)
        image = make_image(queue)

        plt.imshow(image, interpolation='nearest', aspect='auto',
                   extent=[1, 4096, queue_length, 1])
        plt.xlabel('Bin')

        plt.ylabel('Spectra')
        plt.colorbar()
        plt.show()
    else:
        print('Datalog does not exist. ' +
              'Please run manager-D3S.py with datalog enabled.')


if __name__ == '__main__':
    path = decide_path()
    if path == 'None':
        path = DEFAULT_DATALOG_D3S
        sum_graph(path)
        waterfall_graph(path)
    else:
        sum_graph(path)
        waterfall_graph(path)
