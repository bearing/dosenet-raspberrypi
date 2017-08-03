from auxiliaries import datetime_from_epoch
from auxiliaries import set_verbosity
from globalvalues import ANSI_RESET, ANSI_YEL, ANSI_GR, ANSI_RED
from globalvalues import ANSI_BLUE, ANSI_CYAN
from globalvalues import DEFAULT_DATA_BACKLOG_FILE_AQ
from globalvalues import AQ_PM_DISPLAY_TEXT, AQ_P_DISPLAY_TEXT
from globalvalues import BREAK_LINE, TIME_DISPLAY_TEXT, strf
from collections import deque
import socket
import time
import ast
import os
import errno
import csv

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

    def send_to_memory(self, average_data):
        """
        Network is not up
        """
        self.send_to_queue(average_data)
        self.vprint(1, "Network down, saving to queue in memory")

    def regular_send(self, this_end, average_data):
        """
        Normal send
        """
        self.manager.sender.send_data_new_AQ(this_end, average_data)
        if self.queue:
            self.vprint(1, "Flushing memory queue to server")
            while self.queue:
                #print(len(self.queue))
                trash = self.queue.popleft()
                self.manager.sender.send_data_new_AQ(
                    trash[0], trash[1])

    def send_all_to_backlog(self, path=DEFAULT_DATA_BACKLOG_FILE_AQ):
        if self.queue:
            self.vprint(2, "Flushing memory queue to backlog file")
            with open(path, 'a') as f:
                while self.queue:
                    f.write('{0}, '.format(self.queue.popleft()))

    def send_to_queue(self, average_data):
        """
        Adds the time and average_data to the queue object.
        """
        time_string = time.time()
        self.queue.append([time_string, average_data])

    def backlog_to_queue(self, path=DEFAULT_DATA_BACKLOG_FILE_AQ):
        """
        Sends data in backlog to queue and deletes the backlog
        """
        if os.path.isfile(path):
            self.vprint(2, "Flushing backlog file to memory queue")
            with open(path, 'r') as f:
                data = f.read()
            data = ast.literal_eval(data)
            for i in data:
                self.queue.append([i[0], i[1], i[2]])
            print(self.queue)
            os.remove(path)

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

        self.manager.data_log(datalog, average_data=average_data)

        if self.manager.test:
            self.send_to_memory(average_data)
        elif not self.manager.config:
            self.no_config_send(average_data)
        elif not self.manager.publickey:
            self.no_publickey_send(average_data)
        else:
            try:
                self.regular_send(this_end, average_data)
            except (socket.gaierror, socket.error, socket.timeout) as e:
                if e == socket.gaierror:
                    if e[0] == socket.EAI_AGAIN:
                        # TCP and UDP
                        # network is down, but NetworkStatus didn't notice yet
                        # (resolving DNS like dosenet.dhcp.lbl.gov)
                        self.vprint(
                            1,
                            'Failed to send packet! Address resolution error')
                    else:
                        self.vprint(
                            1, 'Failed to send packet! Address error: ' +
                            '{}: {}'.format(*e))
                elif e == socket.error:
                    if e[0] == errno.ECONNREFUSED:
                        # TCP
                        # server is not accepting connections
                        self.vprint(
                            1, 'Failed to send packet! Connection refused')
                    elif e[0] == errno.ENETUNREACH:
                        # TCP and UDP
                        # network is down, but NetworkStatus didn't notice yet
                        # (IP like 131.243.51.241)
                        self.vprint(
                            1, 'Failed to send packet! Network is unreachable')
                    else:
                        # consider handling errno.ECONNABORTED errno.ECONNRESET
                        self.vprint(
                            1, 'Failed to send packet! Socket error: ' +
                            '{}: {}'.format(*e))
                elif e == socket.timeout:
                    # TCP
                    self.vprint(1, 'Failed to send packet! Socket timeout')
                self.send_to_memory(average_data)
