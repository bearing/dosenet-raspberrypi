 #!/usr/bin/python3
# from globalvalues import DEFAULT_DATALOG_D3S

from __future__ import division, print_function
import numpy as np
import matplotlib.pyplot as plt
import Tkinter
# from multiprocessing import Process
from auxiliaries import set_verbosity
# import time
from collections import deque
#import spectra_fitter
# from multiprocessing import Queue as que
import matplotlib.patches as patches
import matplotlib.path as path
import matplotlib.dates as mdates
from dateutil.parser import parse
from datetime import datetime
from datetime import timedelta
import pytz
from matplotlib.backends.backend_pdf import PdfPages
from scipy import optimize
from scipy import asarray as ar,exp
from scipy.integrate import quad
import pandas as pd
import spectra_fitter 
from pandas import DataFrame
import matplotlib.animation as animation
class Real_Time_Spectra(object):
    """
    Class to control the real time spectra plotting
    """

    def __init__(self, manager=None, verbosity=1, logfile=None,
                 resolution=4096):
        """
        Initiate object
        """
        self.v = verbosity
        if manager and logfile is None:
            set_verbosity(self, logfile=manager.logfile)
        else:
            set_verbosity(self, logfile=logfile)

        self.manager = manager

        self.interval = manager.interval
        self.queue = deque()
        self.times = deque()
        self.K_data_counts = deque()
        self.Bi_data_counts = deque()
        self.Tl_data_counts = deque()
        self.maxspectra = manager.maxspectra

        self.data = None
        self.resolution = resolution

        self.first = True

        self.waterfall_drawn = True
        self.isotopes_drawn=True
        # Create a Tkinter window object.
        window_object = Tkinter.Tk()

        # Get the full screen width and height.
        self.screen_width = window_object.winfo_screenwidth()
        self.screen_height = window_object.winfo_screenheight()

        # Destroy the Tkinter window object.
        window_object.destroy()

        # Start up the plotting windows.
        self.start_up()

    def start_up(self):
        '''
        Sets up the new plotting windows.
        '''

        # Turn on interactive mode for plotting to allow for two figure windows
        # to be open at once.
        plt.ion()

        # plt.pause(10)

        # plt.close(0)

        # Setup the plot for the waterfall graph.
        self.waterfall_figure = plt.figure(1)

        plt.xlabel('Bin')
        plt.ylabel('Time (s)')

        # Get the current figure manager for plotting.
        plot_manager = plt.get_current_fig_manager()

        # Set the position and size of the waterfall plot.
        x_pos = int(0.08 * self.screen_width)
        y_pos = int(0.32 * self.screen_height)
        window_width = int(0.36 * self.screen_width)
        window_height = int(0.36 * self.screen_height)

        # Apply the changes to the window geometry.
        plot_manager.window.setGeometry(x_pos, y_pos, window_width, window_height)
        
        self.isotope_figure=plt.figure(3)
        fig=plt.figure(3)
        plot_manager = plt.get_current_fig_manager()
        
        plt.ylim(0,1800)
        plt.xlabel('Time')
        plt.ylabel('counts')
        plt.title('K-40,Bi-214,Tl-208 counts vs Time')
        #plt.legend(bbox_to_anchor=(1.2, 0.05))
        
        #plt.legend(loc='upper center', bbox_to_anchor=(0.5, 1.02,.3,1),
        #  ncol=3, fancybox=True, shadow=False,scatterpoints=1)
                   
        fig.autofmt_xdate()
        plt.show()
        # Set the position and size of the waterfall plot.
        x_pos = int(0.12 * self.screen_width) #originally .08
        y_pos = int(0.32 * self.screen_height)
        window_width = int(0.4 * self.screen_width) #originally .36
        window_height = int(0.4 * self.screen_height)

        # Apply the changes to the window geometry.
        plot_manager.window.setGeometry(x_pos, y_pos, window_width, window_height)
        
        
        # Setup the plot for the spectrum (sum graph).
        self.spectrum_figure = plt.figure(2)

        # plt.xlabel('Channel')
        # plt.ylabel('Counts')

        # # Get the current figure manager for plotting.
        plot_manager = plt.get_current_fig_manager()

        # Set the position and size of the waterfall plot.
        x_pos = int(0.56 * self.screen_width)
        y_pos = int(0.32 * self.screen_height)
        window_width = int(0.36 * self.screen_width)
        window_height = int(0.36 * self.screen_height)

        # Apply the changes to the window geometry.
        plot_manager.window.setGeometry(x_pos, y_pos, window_width, window_height)

        # plt.ioff()

    def add_data(self, spectra,maxspectra):
        """
        Takes data from datalog and places it in a queue. Rebin data here.
        Applies to waterfall plot/isotope plot 
        """
        # Create a new spectrum by binning the old spectrum.
        
        new_spectra = self.rebin(spectra)
        K_counts, Bi_counts, Tl_counts = spectra_fitter.low_stat_isotope_counts(spectra)#should be get_isotope counts
        self.add_isotope_counts(K_counts,Bi_counts,Tl_counts,maxspectra)
        # Add the new spectrum to queue.
        self.queue.append(new_spectra)

        # Save the original size of the data queue.
        data_length = len(self.queue)

        # Pop off the first data point if the total number of counts in the
        # spectrum is more than the count window defined by the sum interval
        # to create a running average.
        if data_length > maxspectra:

            self.queue.popleft()
        self.times.append(datetime.now())
        
        if len(self.times) > maxspectra:
            print('this is inside add_Data',len(self.times))
            self.times.popleft()   
            # # Save the original size of the data queue.
            # data_length = len(data)
            
    def add_isotope_counts(self,K_counts,Bi_counts,Tl_counts,maxspectra):
        self.K_data_counts.append(K_counts)
        self.Bi_data_counts.append(Bi_counts)
        self.Tl_data_counts.append(Tl_counts)
        
        self.data_length1=len(self.K_data_counts)
        self.data_length2=len(self.Bi_data_counts)
        self.data_length3=len(self.Tl_data_counts)
    
        if  self.data_length1 > maxspectra:
            print('this is inside add_isotope_counts',len(self.K_data_counts))
            self.K_data_counts.popleft()
        if  self.data_length2 > maxspectra:
            print('this is inside add_isotope_counts',len(self.Bi_data_counts))
            self.Bi_data_counts.popleft()
        if self.data_length3 > maxspectra:
            print('this is inside add_isotope_counts',len(self.Tl_data_counts))
            self.Tl_data_counts.popleft()
    def run_avg_data(self, data, maxspectra):
        """
        Calculates a running average of all the count data for each bin in the
        queue.
        """
        # Save the original length of the data queue.
        data_length = len(data)

        # Print outs for debugging.
        print('\n\n\tThe data queue length is {}'.format(data_length) + '.\n\n')
        # print('\n\n\tThe data queue: {}'.format(data) + '\n\n')

        # Create a temporary data queue so the data can be summed.
        temp_data = np.array(data)

        # Save the original length of the temporary data queue.
        temp_length = len(temp_data)

        # Print outs for debugging.
        print('\n\n\tThe temporary data array length is {}'.format(temp_length) + '.\n\n')
        # print('\n\n\tThe temporary data array: {}'.format(temp_data) + '\n\n')

        # print(data.shape)

        # Total all the counts in the spectrum.
        # spectrum_sum = np.sum(data)

        # # Append all the data points to the bin sum array.
        # while len(temp) > 0:
        #
        #     self.bin_sum_array += temp.popleft()

        # Define the running average as the mean of each element in the
        #   summation of the spectra in the temporary data array.
        running_avg_array = sum(temp_data) / temp_length
        sum_data= np.sum(temp_data,2)
        return running_avg_array,sum_data
    

    def rebin(self, data, n=4):
        """
        Rebins the array. n is the divisor. Rebin the data in the grab_data
        method.
        """
        a = len(data)/n

        new_data = np.zeros((int(self.resolution/n), 1))

        i = 0

        count = 0

        while i < a:

            temp = sum(data[i:n*(count+1)])

            new_data[count] = temp

            count += 1

            i += n

        return new_data

    def make_image(self):
        """
        Prepares an array for the waterfall plot
        """
        if self.first:

            self.first = False
            self.data = self.fix_array()

        else:

            self.data = np.concatenate((self.fix_array(), self.data), axis=0)

            # Removes oldest spectra to keep size equal to maxspectra
            if len(self.data) > self.maxspectra:

                self.data = self.data[:-1]

    def fix_array(self, n=4):
        """
        Used to format arrays for the waterfall plot.
        """
        new_array = np.zeros((1, int(self.resolution/n)), dtype = float)
        new_array[0, :] = np.ndarray.flatten(self.queue[-1])

        return new_array

    def sum_graph(self,data):
        """
        Prepares plot for sum graph
        """

        # Switch to working on the spectrum figure window.
        plt.figure(2)

        # Set the labels for the spectrum plot.
        plt.xlabel('Channel')
        plt.ylabel('Counts')

        # Resize the spectrum figure window to make room for the axes labels.
        plt.tight_layout()

        # Set a logarithmic y-scale.
        plt.yscale('log')

        # Plot the spectrum plot.
        x = range(0,len(data))
        #x = np.linspace(0, 4096, 256)
        plt.plot(x,
                 data,
                 drawstyle='steps-mid')

        # Show the spectrum plot.
        plt.show()

        # Wait before displaying another plot. Otherwise, wait the specified
        #   number of seconds before continuing with the code execution.
        plt.pause(0.0005)

    def waterfall_graph(self):
        """
        Grabs the data and prepares the waterfall.
        """
        self.make_image()

    def plot_waterfall(self):

        plt.figure(1)

        self.waterfall_graph()

        if self.waterfall_drawn:

            self.waterfall_plot = plt.imshow(self.data,
                                             interpolation='nearest',
                                             aspect='auto',
                                             extent=[1, 4096, 0,
                                                     np.shape(self.data)[0]
                                                     * self.interval])
            # plt.colorbar()

            self.waterfall_drawn = False

        if not self.waterfall_drawn:

            self.waterfall_plot.set_data(self.data)

        # plt.draw()
        plt.show()
        # plt.pause(self.interval)
        plt.pause(0.0005)
        # plt.close()
        
    def plot_isotopes(self,maxspectra=20):
        #Plotting the the three Isotopes on same plot
        
        plt.figure(3)
        temp_K_data_counts=list(self.K_data_counts)
        temp_Bi_data_counts=list(self.Bi_data_counts)
        temp_Tl_data_counts =list(self.Tl_data_counts)
        temp_times=list(self.times)
        
          
        #plt.ion()       # Enable interactive mode
        if self.data_length1 >= maxspectra:
           del temp_K_data_counts[0]
           del temp_Bi_data_counts[0]
           del temp_Tl_data_counts[0]
           del temp_times[0]
           plt.clf()
           #plt.tight_layout()
           plt.xlabel('Time')
           plt.ylabel('counts')
           plt.legend(loc='upper center', bbox_to_anchor=(0.5, 1.02),
                           ncol=3, fancybox=True, shadow=False,numpoints=1)
        #plt.plot_date(times,K_counts,'bo',label='k-40')
        plt.errorbar(temp_times,temp_K_data_counts,yerr=np.sqrt(temp_K_data_counts),fmt='bo',ecolor='b',label='K-40')
        #plt.plot_date(times,Bi_counts,'ro',label='Bi-214')
        plt.errorbar(temp_times, temp_Bi_data_counts,yerr=np.sqrt(temp_Bi_data_counts),fmt='ro',ecolor='r',label='Bi-214')
        #plt.plot_date(times,Tl_counts,'ko',label='Tl-208')
        plt.errorbar(temp_times,temp_Tl_data_counts,yerr=np.sqrt(temp_Tl_data_counts),fmt='ko',ecolor='y',label='Tl-208')

        if self.isotopes_drawn:
                plt.legend(loc='upper center', bbox_to_anchor=(0.5, 1.02),
                           ncol=3, fancybox=True, shadow=False,numpoints=1)
                self.isotopes_drawn = False
        return plt.legend
    # Updating the data point by erasing oldest data from data set on plot using FuncAnimation
    ani = animation.FuncAnimation(plt.figure(3), plot_isotopes, repeat=True, interval=1000)
    
    def plot_sum(self):
        """
        Plot the sum (spectrum) figure.
        """
        # plt.figure(figsize=(25,15))

        plt.figure(2)

        # Get the running average
        self.run_avg,self.sum_data = self.run_avg_data(self.queue, self.maxspectra)

        plt.clf()

        self.sum_graph(self.run_avg)

        self.spectrum_figure.show()
        # plt.pause(self.interval)
        plt.pause(0.0005)
        
        
        # plt.close()
