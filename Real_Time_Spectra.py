#!/usr/bin/python3
#from globalvalues import DEFAULT_DATALOG_D3S

from __future__ import division
import numpy as np
import matplotlib.pyplot as plt
import Tkinter
# from multiprocessing import Process
from auxiliaries import set_verbosity
# import time
from collections import deque


class Real_Time_Spectra(object):
    '''
    Class to control the real time spectra plotting
    '''

    def __init__(self, manager=None, verbosity=1, logfile=None, resolution=256):
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

        self.data = None
        self.resolution = resolution

        self.first = True

        self.waterfall_drawn = True

        # Create a window object.
        window_object = Tkinter.Tk()

        # Get the full screen width and height.
        self.screen_width = window_object.winfo_screenwidth()
        self.screen_height = window_object.winfo_screenheight()

        # Destroy the window object.
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

        self.waterfall_figure

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

        # Setup the plot for the spectrum (sum graph).
        self.spectrum_figure = plt.figure(2)

        self.spectrum_figure

        plt.xlabel('Channel')
        plt.ylabel('Counts')

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

    def get_data(self, spectra):
        """
        Takes data from datalog and places it in a queue. Rebin data here. Applies to Waterfall
        """
        new_spectra = self.rebin(spectra)
        self.manager.wqueue.append(new_spectra)


    def sum_data(self,data):
        """
        Sums up the data in the queue.
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
            self.data = np.zeros((1, self.resolution),dtype=float)
            self.first = False
            temp = self.fix_array(self.manager.wqueue.pop())
            self.data[0, :] = np.ndarray.flatten(temp)
        else:
            temp = self.fix_array(self.manager.wqueue.pop())
            self.data = np.concatenate((np.transpose(temp), self.data), axis=0)

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

        # plt.xlabel('Channel')
        # plt.ylabel('Counts')

        plt.figure(2)

        x = np.linspace(0, 4096, 256)
        plt.plot(x, data, drawstyle='steps-mid')

        plt.show()
        plt.pause(0.6)

    def waterfall_graph(self, spectra):
        """
        Grabs the data and prepares the waterfall.
        """
        self.get_data(spectra)
        self.make_image()


    def plot_waterfall(self, spectra):

        plt.figure(1)

        self.waterfall_graph(spectra)

        if self.waterfall_drawn:

            self.waterfall_plot = plt.imshow(self.data,
                                             interpolation='nearest',
                                             aspect='auto', extent=[1, 4096, \
                                             0, np.shape( self.data )[0] * \
                                             self.interval])
            plt.colorbar()

            self.waterfall_drawn = False

        if not self.waterfall_drawn:

            self.waterfall_plot.set_data(self.data)

        # plt.draw()
        plt.show()
        # plt.pause(self.interval)
        plt.pause(0.0005)
        # plt.close()

    def plot_sum(self,spectra):

        # plt.figure(figsize=(25,15))

        plt.figure(2)

        self.get_data(spectra)

        total = self.sum_data(deque(self.manager.wqueue))

        plt.clf()

        self.sum_graph(total)

        self.spectrum_figure.show()
        # plt.pause(self.interval)
        plt.pause(0.0005)

        # plt.close()
