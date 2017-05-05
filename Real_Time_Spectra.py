#!/usr/bin/python3
#from globalvalues import DEFAULT_DATALOG_D3S
import numpy as np
#matplotlib.use("Qt5Agg")
import matplotlib.pyplot as plt
from multiprocessing import Process
from auxiliaries import set_verbosity
import time

class Real_Time_Spectra(object):

    def __init__(self, manager=None, verbosity=1, logfile=None,resolution=256):
        '''
        Initiate object
        '''
        self.v = verbosity
        if manager and logfile is None:
            set_verbosity(self, logfile=manager.logfile)
        else:
            set_verbosity(self, logfile=logfile)
            
        self.manager = manager

        self.interval = manager.interval

        self.image = None
        self.resolution = resolution
        
        self.first = True

    def get_data(self, spectra):
        """
        Takes data from datalog and places it in a queue. Rebin data here. Applies to Waterfall
        """
        new_spectra = self.rebin(spectra)
        self.manager.wqueue.append(new_spectra)


    def sum_data(self,data):
        """
        Sums up the data in the queue
        """
        total = data.popleft()
        i = 1
        while i < len(data):
            total += data.popleft()
            i+=1
        return total


    def rebin(self,data, n=4):
        """
        Rebins the array. n is the divisor. Rebin the data in the grab_data method. 
        """
        a = len(data)/n
        new_data = np.zeros((self.resolution, 1))
        i = 0 
        count = 0
        while i < a:
            temp = sum(data[i:n*(count+1)])
            new_data[count] = temp
            count+=1
            i+=n
        return new_data



    def make_image(self):
        """
        Prepares an array for the waterfall plot
        """
        if self.first:
            self.image = np.zeros((1, self.resolution),dtype=float)
            self.first = False
            temp = self.fix_array(self.manager.wqueue.pop())
            self.image[0, :] = np.ndarray.flatten(temp)
        else:
            temp = self.fix_array(self.manager.wqueue.pop())
            self.image = np.concatenate((np.transpose(temp), self.image), axis=0)
        


    def fix_array(self, array):
        """
        Used to format arrays for the waterfall plot. 
        """
        new_array = array.copy()[:self.resolution]
        return new_array
            
    def sum_graph(self,data):
        """
        Prepares plot for sum graph
        """

        plt.xlabel('Channel')
        plt.ylabel('Counts')
        x = np.linspace(0, 4096, 256)
        plt.plot(x, data, drawstyle='steps-mid')

        #plt.show()
        plt.pause(0.6)

    def waterfall_graph(self,spectra):
        """
        Grabs the data and prepares the waterfall.
        """
        self.get_data(spectra)
        self.make_image()


    def plot_waterfall(self,spectra):

        plt.figure(figsize=(25,15))
        plt.xlabel('Bin')
        plt.ylabel('Time (s)')
        self.waterfall_graph(spectra)
        plt.imshow(self.image, interpolation='nearest', aspect='auto',
                        extent=[1, 4096, 0, np.shape(self.image)[0]*self.interval])
        plt.colorbar()
        plt.draw()
        plt.pause(self.interval)
        plt.close()

    def plot_sum(self,spectra):

        plt.figure(figsize=(25,15))
        queue = get_data(spectra)
        total = sum_data(queue)
        plt.clf()
        self.sum_graph(total)
        plt.pause(self.interval)
        plt.close()
    
