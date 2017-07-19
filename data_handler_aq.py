from auxiliaries import datetime_from_epoch
from auxiliaries import set_verbosity
from globalvalues import ANSI_RESET, ANSI_YEL, ANSI_GR, ANSI_RED
from globalvalues import ANSI_BLUE, ANSI_CYAN
from globalvalues import DEFAULT_DATA_BACKLOG_FILE_AQ
from collections import deque
import socket
import time
import ast
import os
import errno
import csv

AQ_PM_DISPLAY_TEXT = (
	'{cyan} {{variable}} = {reset}' +
	'{green} {{avg_data}} {reset}' +
    '{cyan} ug/m3 {reset}').format(
    cyan=ANSI_CYAN, reset=ANSI_RESET, green=ANSI_GR)

AQ_P_DISPLAY_TEXT = (
	'{cyan} # of Particles over {{variable}} = {reset}' +
	'{green} {{avg_data}} {reset}').format(
    cyan=ANSI_CYAN, reset=ANSI_RESET, green=ANSI_GR)

TIME_DISPLAY_TEXT = (
    '{red} This list of average data was gathered from: {reset}' +
    '{yellow}{{start_time}} to {{end_time}}{reset}').format(
    red=ANSI_RED, reset=ANSI_RESET, yellow=ANSI_YEL)

BREAK_LINE = (
    '\n{blue}-----------------------------------------------------------\n{reset}' +
    '\n{blue}-----------------------------------------------------------\n{reset}').format(
    blue=ANSI_BLUE, reset=ANSI_RESET)
strf = '%H:%M:%S'

class Data_Handler_AQ(object):
    """
    Object for sending the data from the Air Quality
    sensor to the server.

    Also handles writing data to datalog and storing
    data to the memory
    """

    def __init__(self,
                 manager=None,
                 verbosity=1,
                 logfile=None,
                 variables=None,
                 ):

        self.v = verbosity
        if manager and logfile is None:
            set_verbosity(self, logfile=manager.logfile)
        else:
            set_verbosity(self, logfile=logfile)

        self.manager = manager
        self.queue = deque('')

        self.variables = variables

    """
    The average_data list has elements comprised of:

    PM01 = Concentration of Particulate Matter less than 1.0um in ug/m3
    PM25 = Concentration of Particulate Matter less than 2.5um in ug/m3
    PM10 = Concentration of Particulate Matter less than 10um in ug/m3

    P03 = Number of paricles in 0.1 L of air over a diameter of 0.3um
    P05 = Number of paricles in 0.1 L of air over a diameter of 0.5um
    P10 = Number of paricles in 0.1 L of air over a diameter of 1.0um
    P25 = Number of paricles in 0.1 L of air over a diameter of 2.5um
    P50 = Number of paricles in 0.1 L of air over a diameter of 5.0um
    P100 = Number of paricles in 0.1 L of air over a diameter of 10um
    """

    def test_send(self, average_data):
        """
        Test Mode
        """
        self.vprint(
            1, ANSI_RED + " * Test mode, not sending to server * " +
            ANSI_RESET)

    def no_config_send(self, average_data):
        """
        Configuration file not present
        """
        self.vprint(1, "Missing config file, not sending to server")

    def no_publickey_send(self, average_data):
        """
        Publickey not present
        """
        self.vprint(1, "Missing public key, not sending to server")

    def regular_send(self, this_end, average_data):
        """
        Normal send
        """
        self.manager.sender.send_data_new_AQ(this_end, P03, P05,
            P10, P25, P50, P100, PM01, PM25, PM10)
        #print(self.queue)
        if self.queue:
            self.vprint(1, "Flushing memory queue to server")
            while self.queue:
                #print(len(self.queue))
                trash = self.queue.popleft()
                self.manager.sender.send_data_new_AQ(
                    trash[0], trash[1], trash[2], trash[3],
                    trash[4], trash[5], trash[6], trash[7],
                    trash[8], trash[9])

    def main(self, datalog, average_data, this_start, this_end):
        """
        Determines how to handle the average air quality data
        """
        start_text = datetime_from_epoch(this_start).strftime(strf)
        end_text = datetime_from_epoch(this_end).strftime(strf)

        self.vprint(
            1, TIME_DISPLAY_TEXT.format(
                start_time=start_text,
                end_time=end_text))
        for i in range(3):
        	self.vprint(
                1, AQ_PM_DISPLAY_TEXT.format(
                    variable=self.variables[i],
                    avg_data=average_data[i]))
        for i in range(3, 9):
        	self.vprint(
                1, AQ_P_DISPLAY_TEXT.format(
                    variable=self.variables[i],
                    avg_data=average_data[i]))
        self.vprint(
            1, BREAK_LINE)
