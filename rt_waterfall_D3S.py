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
        
        self.on = True
        self.first_try = True
    
    def get_data(self, spectra, queue1, queue2):
        new_spectra = self.rebin(spectra)
        queue2.append(new_spectra)
        self.queuelength = len(queue2)
        queue1 = queue2
        print(queue1[0])
   
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
     
    def reset_queue(self, queue1, queue2): 
        for i in queue2: 
            queue1.append(i)
      
    def make_image(self, queue1, queue2):
        """
        Prepares an array for the waterfall plot
        """

        self.image = np.zeros((self.queue_length, 256),dtype=float)
        print(self.queue_length)
        print(len(queue1))
        j = 0
        while j < self.queue_length:
            i = 0
            temp = self.fix_array(queue1.popleft())
            while i < 256:
                self.image[j][i] = temp[i]
                i += 1
            j+=1
      
    def waterfall_graph(self, spectra, queue1, queue2):
        """
        Plots a waterfall graph of all the spectra.
        """
        self.get_data(spectra, queue1, queue2)
        self.queue_length = len(queue2)
        self.make_image(queue1, queue2)
      
    def start_up(self):
        plt.ion()
        plt.xlabel('Bin')
        plt.ylabel('Spectra')
    
    def plot(self, spectra, queue1, queue2):
        if self.first_try:
            self.start_up()
            self.waterfall_graph(spectra, queue1, queue2)
            plt.imshow(self.image, interpolation='nearest', aspect='auto',
                        extent=[1, 4096, self.queuelength, 1])
            plt.show()

            self.first_try = False
        else:
            self.waterfall_graph(spectra, queue1, queue2)
            plt.imshow(self.image, interpolation='nearest', aspect='auto',
                        extent=[1, 4096, self.queuelength, 1])

            plt.show()
