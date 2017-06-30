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
# from multiprocessing import Queue as que


class Real_Time_Spectra(object):
    """
    Class to control the real time spectra plotting
    """

    def __init__(self, manager=None, verbosity=1, logfile=None,
                 resolution=256):
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

        self.maxspectra = manager.maxspectra

        self.data = None
        self.resolution = resolution

        self.first = True

        self.waterfall_drawn = True

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

    def add_data(self, spectra, maxspectra):
        """
        Takes data from datalog and places it in a queue. Rebin data here.
        Applies to waterfall plot.
        """
        # Create a new spectrum by binning the old spectrum.
        new_spectra = self.rebin(spectra)

        # Add the new spectrum to queue.
        self.queue.append(new_spectra)

        # Save the original size of the data queue.
        data_length = len(self.queue)

        # Pop off the first data point if the total number of counts in the
        # spectrum is more than the count window defined by the sum interval
        # to create a running average.
        if data_length > maxspectra:

            self.queue.popleft()

            # # Save the original size of the data queue.
            # data_length = len(data)

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

        return running_avg_array


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

            self.data = np.zeros((1, self.resolution), dtype=float)

            print(self.data)

            self.first = False

            temp = self.fix_array(np.array(self.queue))

            print(temp)

            self.data[0, :] = np.ndarray.flatten(temp)

        else:

            temp = self.fix_array(self.queue)

            self.data = np.concatenate((np.transpose(temp),
                                        self.data), axis=0)

    def fix_array(self, array):
        """
        Used to format arrays for the waterfall plot.
        """
        new_array = array.copy()[0][:self.resolution]
        return new_array

    def sum_graph(self,data):
        """
        Prepares plot for sum graph
        """

        plt.figure(2)

        plt.xlabel('Channel')
        plt.ylabel('Counts')

        plt.yscale('log')

        x = np.linspace(0, 4096, 256)
        plt.plot(x,
                 data,
                 drawstyle='steps-mid')

        plt.show()
        plt.pause(0.6)

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

    def plot_sum(self):
        """
        Plot the sum (spectrum) figure.
        """

        # plt.figure(figsize=(25,15))

        plt.figure(2)

        # Get the running average
        run_avg = self.run_avg_data(self.queue, self.maxspectra)

        plt.clf()

        self.sum_graph(run_avg)

        self.spectrum_figure.show()
        # plt.pause(self.interval)
        plt.pause(0.0005)

        # plt.close()
