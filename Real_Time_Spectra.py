#!/usr/bin/python3
from __future__ import division, print_function
# from globalvalues import DEFAULT_DATALOG_D3S
import numpy as np
# from pandas import DataFrame
# import matplotlib
# matplotlib.use('Qt4Agg')
import matplotlib.pyplot as plt
# import seaborn as sns
# from ggplot import *
from mpltools import style
from mpltools import layout

# import Tkinter
# from PySide.QtGui import QApplication
from PyQt5.QtWidgets import QApplication

from auxiliaries import set_verbosity
from collections import deque


class Real_Time_Spectra(object):
    """
    Class to control the real time spectra plotting
    """

    def __init__(self, manager=None, verbosity=1, logfile=None,
                 resolution=256):
        """Initiate class variables."""

        self.v = verbosity
        if manager and logfile is None:
            set_verbosity(self, logfile=manager.logfile)
        else:
            set_verbosity(self, logfile=logfile)


        self.manager = manager

        self.interval = manager.interval
        self.queue = deque()

        self.maxspectra = manager.maxspectra

        self.data = None
        self.resolution = resolution

        self.first = True

        self.colorbar_drawn = True
        

    def setup_window_geo(self, x_pos_scaling=0.0, y_pos_scaling=0.0, \
                         width_scaling=1.0, height_scaling=1.0):
        '''
        Setup the geometry (position and size) of the last initialized figure
        window.

        Default: Top-left corner position and fullscreen size
        '''

        '''
        Get the current figure manager for plotting.
        '''
        plot_manager = plt.get_current_fig_manager()

        '''
        Set the position and size of the waterfall plot based on the input
        scaling values.
        '''
        x_pos = int(x_pos_scaling * self.screen_width)
        y_pos = int(y_pos_scaling * self.screen_height)
        width = int(width_scaling * self.screen_width)
        height = int(height_scaling * self.screen_height)

        '''
        Apply the changes to the window geometry.if self.colorbar_drawn:

            self.cb = plt.colorbar()
            self.colorbar_drawn = False

        if not self.colorbar_drawn:

            self.cb.remove()
            self.cb = plt.colorbar()

        '''
        plot_manager.window.setGeometry(x_pos, y_pos, width, height)

    def start_up_plotting(self):
        '''Set up the new plotting windows using mpltools with a ggplot theme'''

        '''
        Create a QApplication so we can use PySide to find the screen size.
        '''
        app = QApplication([])

        '''
        Get the screen geometry
        '''
        scr_geo = app.desktop().screenGeometry()

        '''
        Return the screen width and height (in pixels) from the attributes of
        the screen geometry.
        '''
        self.screen_width, self.screen_height = scr_geo.width(), scr_geo.height()

        '''
        Use the ggplot style available though the mpltools layout method.
        '''
        style.use('ggplot')

        """
        Removes toolbar from figures.
        """
        plt.rcParams['toolbar'] = 'None'

        '''
        Turn on interactive mode for plotting to allow for two figure windows
        to be open at once.
        '''
        plt.ion()

        '''
        Setup the plot for the waterfall graph.
        '''
        plt.figure(1)

        '''
        Label the axes.
        '''
        plt.xlabel('Bin')
        plt.ylabel('Time (s)')

        '''
        Change the window geometry (position and size) using the proper scaling
        factors.
        '''
        self.setup_window_geo(0.08, 0.32, 0.36, 0.36)

        '''
        Draw the blank canvas figure for the spectrum plot and store it as the
        second figure window.
        '''
        plt.figure(2)

        '''
        Change the window geometry (position and size) using the proper scaling
        factors.
        '''
        self.setup_window_geo(0.56, 0.32, 0.36, 0.36)

    def add_data(self, queue, spectra, maxspectra):
        """
        Takes data from datalog and places it in a queue. Rebin data here.
        Applies to waterfall plot.
        """

        '''
        Create a new spectrum by binning the old spectrum.
        '''
        new_spectra = self.rebin(spectra)

        '''
        Add the new spectrum to queue.
        '''
        queue.append(new_spectra)

        '''
        Save the original size of the data queue.
        '''
        data_length = len(queue)

        '''
        Pop off the first data point if the total number of counts in the
        spectrum is more than the count window defined by the sum interval
        to create a running average.
        '''
        print("Real_Time_Spectra: Data length is {}, spectra sum is {}".format(data_length, sum(new_spectra)))
        if data_length > maxspectra:

            queue.popleft()

    def run_avg_data(self, data, maxspectra):
        """
        Calculates a running average of all the count data for each bin in the
        queue.
        """

        '''
        Save the original length of the data queue.
        '''
        data_length = len(data)

        '''
        Create a temporary data queue so the data can be summed.
        '''
        temp_data = np.array(data)

        '''
        Save the original length of the temporary data queue.
        '''
        temp_length = len(temp_data)

        '''
        Calculate the running average as the mean of each element in the
        summation of the spectra in the temporary data array.
        '''
        running_avg_array = sum(temp_data) / temp_length

        '''
        Calculate the sum of the spectra.
        '''
        sum_data = sum(temp_data)

        '''
        Return the running average and summation data.
        '''
        return running_avg_array, sum_data

    def rebin(self, data, n=4):
        """
        Rebins the array. n is the divisor. Rebin the data in the grab_data
        method.
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

    def make_image(self):
        """
        Prepares an array for the waterfall plot
        """
        if self.first:

            self.first = False
            self.data = self.fix_array()

        else:

            self.data = np.concatenate((self.fix_array(), self.data), axis=0)

            '''
            Removes oldest spectra to keep size equal to maxspectra
            '''
            if len(self.data) > self.maxspectra:

                self.data = self.data[:-1]

    def fix_array(self):
        """
        Used to format arrays for the waterfall plot.
        """
        new_array = np.zeros((1, self.resolution), dtype = float)
        new_array[0, :] = np.ndarray.flatten(self.queue[-1])

        return new_array

    def sum_graph(self, data):
        """Prepares plot for sum graph."""

        '''
        Switch to working on the spectrum figure window.
        '''
        plt.figure(2)

        '''
        Set the labels for the spectrum plot.
        '''
        plt.xlabel('Channel')
        plt.ylabel('Counts')

        '''
        Resize the plot to make room for the axes labels without resizing the
        figure window.
        '''
        plt.tight_layout()

        '''
        Set a logarithmic y-scale.
        '''
        plt.yscale('log')

        '''
        Create the x-axis data for the spectrum plot.
        '''
        x = np.linspace(0, 4096, 256)

        '''
        Plot the spectrum plot.
        '''
        plt.plot(x, data, drawstyle='steps-mid')

        '''
        Show the spectrum plot.
        '''
        plt.show()

        '''
        Wait before displaying another plot. Otherwise, wait the specified
        number of seconds before continuing with the code execution.
        '''
        plt.pause(0.0005)

    def plot_waterfall(self):
        plt.figure(1)
        """
        Grabs the data for waterfall plot.
        """
        self.make_image()
        """
        Plots the data for the waterfall plot.
        """
        self.waterfall_plot = plt.imshow(self.data,
                                         interpolation='nearest',
                                         aspect='auto',
                                         extent=[1, 4096, 0,
                                         np.shape(self.data)[0]
                                         * self.interval])
        """
        Updates the colorbar by removing old colorbar.
        """
        
        if self.colorbar_drawn:

            self.cb = plt.colorbar()
            self.colorbar_drawn = False

        if not self.colorbar_drawn:

            self.cb.remove()
            self.cb = plt.colorbar()

        plt.tight_layout()

        plt.show()
        
        plt.pause(0.0005)

    def plot_sum(self):
        """
        Plot the sum (spectrum) figure.
        """

        # plt.figure(figsize=(25,15))

        '''
        Point to the figure window for the spectrum plot.
        '''
        plt.figure(2)

        '''
        Get the running average
        '''
        print("Data is {}".format(self.queue))
         
        run_avg, self.sum_data = self.run_avg_data(self.queue, self.maxspectra)

        '''
        Clear the prior spectrum figure.
        '''
        plt.clf()
        

        '''
        Plot the spectrum figure
        '''
        self.sum_graph(run_avg)

        '''
        Show the updated spectrum figure window.
        '''
        plt.show()

        '''
        Pause before displaying the next figure window.
        '''
        plt.pause(0.0005)

        # plt.close()
