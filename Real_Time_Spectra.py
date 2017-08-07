#!/usr/bin/python3
from __future__ import division, print_function
# from globalvalues import DEFAULT_DATALOG_D3S
import numpy as np
# from pandas import DataFrame
import matplotlib
matplotlib.use('GTKAgg')
# matplotlib.use('TkAgg')
# matplotlib.use('Qt4Agg')
import matplotlib.pyplot as plt

import gc

from mpltools import style
# from mpltools import layout

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

        '''
        Initialize the verbosity.
        '''
        self.v = verbosity

        '''
        Set the verbosity if there is no manager or logfile.
        '''
        if manager and logfile is None:
            set_verbosity(self, logfile=manager.logfile)
        else:
            set_verbosity(self, logfile=logfile)

        '''
        Set the class manager equal to the manager using this class.
        '''
        self.manager = manager

        '''
        Set the interval equal to the interval value from the manager.
        '''
        self.interval = manager.interval

        '''
        Initialize a queue to hold the spectra.
        '''
        self.queue = deque()

        '''
        Set the maximum number of spectra equal to the value from the manager.
        '''
        self.maxspectra = manager.maxspectra

        '''
        Initialize the waterfall data.
        '''
        self.data = None

        '''
        Initialize the resolution (number of lines in each horizontal 'strip'
        of the waterfall).
        '''
        self.resolution = resolution

        '''
        Initialize the variable used to check if the first waterfall needs to
        be drawn.
        '''
        self.first_waterfall = True

        # self.first_colorbar = True

        '''
        Initialize the variable to check if the waterfall has been drawn.
        '''
        self.waterfall_drawn = False

        '''
        Initialize the variable to check if the spectrum has been drawn.
        '''
        self.spectrum_drawn = False

        '''
        Start up the plotting windows.
        '''
        self.start_up_plotting()

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
        Apply the changes to the window geometry.
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
        Show the blank plot without blocking further changes to the figure
        window. Allows for fast updating of the figure later.
        '''
        plt.show(block=False)

        # '''
        # Draw the blank canvas figure for the spectrum plot and store it as the
        # second figure window.
        # '''
        # plt.figure(2), \
        #     (self.spectrum_plot_axis, \
        #      self.spectrum_sumplot_axis) = plt.subplots(2, 1,
        #                                 gridspec_kw={'nrows': 2,
        #                                              'ncols': 1,
        #                                              'height_ratios': [4, 1]})

        '''
        Setup the figure window for the spectrum graph.
        '''
        plt.figure(2)

        '''
        Add a subplot to the figure window so we can add artists to it.
        '''
        self.spectrum_axis = plt.figure(2).add_subplot(1, 1, 1)

        '''
        Change the window geometry (position and size) using the proper scaling
        factors.
        '''
        self.setup_window_geo(0.56, 0.32, 0.36, 0.36)

        '''
        Show the blank plot without blocking further changes to the figure
        window. Allows for fast updating of the figure later.
        '''
        plt.show(block=False)

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

        print(temp_data.shape)

        '''
        Save the original length of the temporary data queue.
        '''
        temp_length = len(temp_data)

        '''
        Calculate the running average as the mean of each element in the
        summation of the spectra in the temporary data array.
        '''
        running_avg_array = sum(temp_data) / temp_length

        print(running_avg_array.shape)

        '''
        Calculate the sum of the spectra.
        '''
        sum_data = np.sum(temp_data, 1)

        print(sum_data.shape)

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
        if self.first_waterfall:

            self.first_waterfall = False
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

    def sum_graph(self, avg_data, sum_data):
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
        self.spectrum_bins = np.linspace(0, 4096, 256)

        '''
        Plot the spectrum plot.
        '''
        plt.plot(self.spectrum_bins, avg_data, drawstyle='steps-mid')

    def plot_waterfall(self):

        '''
        Switch to the waterfall figure window.
        '''
        plt.figure(1)

        '''
        Clear the prior spectrum figure.
        '''
        plt.clf()

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
        # """
        # Updates the colorbar by removing old colorbar.
        # """
        # if self.first_colorbar:
        #
        #     self.cb = plt.colorbar()
        #     self.first_colorbar = False
        #
        # if not self.first_colorbar:
        #
        #     self.cb.remove()
        #     self.cb = plt.colorbar()

        '''
        Add a colorbar.
        '''
        plt.colorbar()

        '''
        Resize the plot so the figure window can fit both it and the axes to
        the plot.
        '''
        plt.tight_layout()

        '''
        Update the figure window with the new waterfall plot.
        '''
        plt.figure(1).canvas.update()

        '''
        Refresh the Qt events used to create the canvas.
        '''
        plt.figure(1).canvas.flush_events()

        '''
        Collect and remove the figure window cache.
        '''
        gc.collect()

    def plot_sum(self):
        """
        Plot the sum (spectrum) figure.
        """
        '''
        Get the running average
        '''
        avg_data, sum_data = self.run_avg_data(self.queue, self.maxspectra)

        '''
        Point to the figure window for the spectrum plot.
        '''
        plt.figure(2)

        '''
        Clear the prior spectrum figure.
        '''
        plt.clf()

        # '''
        # Plot the spectrum figure fresh if it hasn't been plotted before.
        #
        # Otherwise, just update the x and y data, restore the background to the
        # plot, redraw the plot contents and fill the plot window.
        # '''
        # if self.spectrum_drawn == False:
        #
        #     '''
        #     Plot the spectrum graph.
        #     '''
        #     self.sum_graph(avg_data, sum_data)
        #
        #     '''
        #     Show the spectrum graph.
        #     '''
        #     plt.show(block=False)
        #
        #     '''
        #     Draw the figure canvas.
        #     '''
        #     plt.figure(2).canvas.draw()
        #
        #     '''
        #     Store the background to the spectrum plot.
        #     '''
        #     self.spectrum_background = plt.figure(2).canvas.copy_from_bbox(self.spectrum_axis.bbox)
        #
        #     '''
        #     Ensure the entire plot isn't replotted again.
        #     '''
        #     self.spectrum_drawn = True
        #
        # else:
        #
        #     '''
        #     Set new plot data.
        #     '''
        #     self.spectrum_plot.set_data(self.spectrum_bins, avg_data)
        #
        #     '''
        #     Restore the background region of the spectrum plot.
        #     '''
        #     plt.figure(2).canvas.restore_region(self.spectrum_background)
        #
        #     '''
        #     Redraw the artist corresponding to the spectrum shape only.
        #     '''
        #     self.spectrum_axis.draw_artist(self.spectrum_plot)
        #
        #     '''
        #     Copy over the new figure from the old one and only change what has
        #     been changed.
        #     '''
        #     plt.figure(2).canvas.blit(self.spectrum_axis.bbox)

        '''
        Update the plot with the new spectrum.
        '''
        plt.figure(2).canvas.update()

        '''
        Refresh the Qt events used to create the canvas.
        '''
        plt.figure(2).canvas.flush_events()

        '''
        Collect and remove the figure window cache.
        '''
        gc.collect()
