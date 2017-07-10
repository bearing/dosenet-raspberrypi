from auxiliaries import datetime_from_epoch
from auxiliaries import set_verbosity
from globalvalues import ANSI_RESET, ANSI_YEL, ANSI_GR, ANSI_RED
from globalvalues import DEFAULT_DATA_BACKLOG_FILE_AQ
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
                 ):

        self.v = verbosity
        if manager and logfile is None:
            set_verbosity(self, logfile=manager.logfile)
        else:
            set_verbosity(self, logfile=logfile)

        self.manager = manager
        self.queue = deque('')
