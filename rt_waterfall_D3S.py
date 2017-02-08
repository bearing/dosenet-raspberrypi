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
                ):
        
        self.v = verbosity
        if manager and logfile is None:
            set_verbosity(self, logfile=manager.logfile)
        else:
            set_verbosity(self, logfile=logfile)
            
        self.manager = manager
        
        self.interval = manager.interval
        
        self.queuelength = None
        self.image = None
    
    def get_data(self, spectra):
        new_spectra = self.rebin(spectra)
        self.manager.wqueue2.append(new_spectra)
        self.queuelength = len(self.manager.wqueue2)
        for i in self.manager.wqueue2:
            self.manager.wqueue1.append(i)
   
    def rebin(self, data, n=4):
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

    def fix_array(self, array):
        """
        Used to format arrays for the waterfall plot.Called inside make_image.
        """
        new_array = np.zeros((256))
        i = 0
        while i < 256:
            new_array[i] = array[i]
            i += 1
        return new_array
      
    def make_image(self):
        """
        Prepares an array for the waterfall plot
        """

        self.image = np.zeros((self.queuelength, 256),dtype=float)
        j = 0
        while j < self.queuelength:
            i = 0
            temp = self.fix_array(self.manager.wqueue1.popleft())
            while i < 256:
                self.image[j][i] = temp[i]
                i += 1
            j+=1
      
    def waterfall_graph(self, spectra):
        """
        Plots a waterfall graph of all the spectra.
        """
        self.get_data(spectra)
        self.make_image()
      
    def start_up(self):
        plt.xlabel('Bin')
        plt.ylabel('Spectra')
    
    def plot(self, spectra):
        self.start_up()
        self.waterfall_graph(spectra)
        plt.imshow(self.image, interpolation='nearest', aspect='auto',
                    extent=[1, 4096, 0, self.queuelength])
        plt.draw()
        plt.pause(self.interval)
        plt.close()
