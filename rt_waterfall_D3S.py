from auxiliaries import set_verbosity
import time

import numpy as np
import matplotlib.pyplot as plt

class Rt_Waterfall_D3S(object):
    """
    Class for running the D3S in real-time waterfall mode
    """
    
    def __init__(self, 
                 manager=None, 
                 verbosity=1,
                 logfile=None,
                 resolution=256
                ):
        
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
        
        self.start_up()
    
    def get_data(self, spectra):
        '''
        Transfers spectra data to 2 queues that were designed for 
        real time waterfall mode.
        Call rebin spectra in this method.
        '''
        new_spectra = self.rebin(spectra)
        self.manager.wqueue.append(new_spectra)
   
    def rebin(self, data, n=4):
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
            count += 1
            i += n
        return new_data

    def fix_array(self, array):
        """
        Used to format arrays for the waterfall plot.
        Called inside make_image.
        """
        new_array = array.copy()[:self.resolution]
        return new_array
      
    def make_image(self):
        """
        Prepares an array for the waterfall plot
        Call fix_array in this method
        """
        if self.first:
            self.image = np.zeros((1, self.resolution),dtype=float)
            self.first = False
            temp = self.fix_array(self.manager.wqueue.pop())
            self.image[0, :] = np.ndarray.flatten(temp)
        else:
            temp = self.fix_array(self.manager.wqueue.pop())
            self.image = np.concatenate((np.transpose(temp), self.image), axis=0)
      
    def waterfall_graph(self, spectra):
        """
        Grabs the data and prepares the waterfall.
        """
        self.get_data(spectra)
        self.make_image()
      
    def start_up(self):
        '''
        Sets up the parameters for the plotting window
        '''
        plt.ion()
        plt.figure(figsize=(25,15))
        plt.xlabel('Bin')
        plt.ylabel('Time (s)')
        plt.title('Waterfall Plot: Interval of {} Seconds'.format(self.interval))
    
    def plot(self, spectra):
        '''
        Actually plots the spectra
        '''
        #self.start_up()
        self.waterfall_graph(spectra)
        plt.imshow(self.image, interpolation='nearest', aspect='auto',
                    extent=[1, 4096, 0, np.shape(self.image)[0]*self.interval])
        plt.colorbar()
        #plt.draw()
        plt.show()
        plt.pause(self.interval)
        #plt.close()
