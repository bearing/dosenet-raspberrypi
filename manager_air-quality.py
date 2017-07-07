import time
import argparse
import signal
import sys
import serial
import csv

from globalvalues import RPI
if RPI:
    import RPi.GPIO as GPIO

from sender import ServerSender
from data_handler import Data_Handler_AQ

from globalvalues import DEFAULT_CONFIG, DEFAULT_PUBLICKEY
from globalvalues import DEFAULT_HOSTNAME, DEFAULT_UDP_PORT, DEFAULT_TCP_PORT
from globalvalues import DEFAULT_SENDER_MODE
from globalvalues import DEFAULT_DATALOG_AQ
from globalvalues import DEFAULT_INTERVAL_NORMAL_AQ

class Manager_AQ(object):

    def __init__(self,
                 interval=None,
                 sender_mode=DEFAULT_SENDER_MODE,
                 verbosity=None,
                 log=False,
                 logfile=None,
                 datalog=None,
                 datalogflag=False,
                 config=None,
                 hostname=DEFAULT_HOSTNAME,
                 port=None,
                 test=None,
                 ):

        self.interval = interval

        self.datalog = datalog
        self.datalogflag = datalogflag

        self.a_flag()
        self.d_flag()
        self.make_data_log(self.datalog)

        self.data_handler = Data_Handler_AQ(
            manager=self,
            verbosity=self.v,
            logfile=self.logfile)
        self.sender = ServerSender(
            manager=self,
            mode=sender_mode,
            port=port,
            verbosity=self.v,
            logfile=self.logfile)

        self.test = test

        self.data_handler.backlog_to_queue()

    def a_flag(self):
        """
        Checks if the -a from_argparse is called.
        If it is called, sets the path of the data-log to
        DEFAULT_DATALOG_D3S.
        """
        if self.datalogflag:
            self.datalog = DEFAULT_DATALOG_AQ

    def d_flag(self):
        """
        Checks if the -d from_argparse is called.
        If it is called, sets datalogflag to True.
        """
        if self.datalog:
            self.datalogflag = True

    def make_data_log(self, file):
        if self.datalogflag:
            with open(file, 'a') as f:
                pass
