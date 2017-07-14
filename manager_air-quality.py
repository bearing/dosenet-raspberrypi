import time
import argparse
import signal
import sys
import serial
import csv
import datetime

from globalvalues import RPI
if RPI:
    import RPi.GPIO as GPIO

from sender import ServerSender
from data_handler_aq import Data_Handler_AQ

from globalvalues import DEFAULT_CONFIG, DEFAULT_PUBLICKEY
from globalvalues import DEFAULT_HOSTNAME, DEFAULT_UDP_PORT, DEFAULT_TCP_PORT
from globalvalues import DEFAULT_SENDER_MODE
from globalvalues import DEFAULT_DATALOG_AQ
from globalvalues import DEFAULT_INTERVAL_NORMAL_AQ
from globalvalues import DEFAULT_AQ_PORT

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
                 publickey=None,
                 hostname=DEFAULT_HOSTNAME,
                 port=None,
                 test=None,
                 AQ_port=DEFAULT_AQ_PORT,
                 ):

        self.interval = interval

        self.aq-port = AQ_port

        self.datalog = datalog
        self.datalogflag = datalogflag

        self.a_flag()
        self.d_flag()
        self.make_data_log(self.datalog)

        self.handle_input(
            log, logfile, verbosity, interval, config, publickey)

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

    def handle_input(self, log, logfile, verbosity, interval,
                     config, publickey):

        if log and logfile is None:
            logfile = DEFAULT_LOGFILE_AQ

        if logfile and not log:
            log = True

        if log:
            self.logfile = logfile
        else:
            self.logfile = None

        if verbosity is None:
            verbosity = 1

        self.v = verbosity
        set_verbosity(self, logfile=logfile)

        if log:
            self.vprint(1, '')
            self.vprint(1, 'Writing to logfile at {}'.format(self.logfile))
        self.running = False

        if interval is None:
            self.vprint(
                2, "No interval given, using interval at 5 minutes")
            interval = DEFAULT_INTERVAL_NORMAL_AQ
        if config is None:
            self.vprint(2, "No config file given, " +
                        "attempting to use default config path")
            config = DEFAULT_CONFIG
        if publickey is None:
            self.vprint(2, "No publickey file given, " +
                        "attempting to use default publickey path")
            publickey = DEFAULT_PUBLICKEY

        self.interval = interval

        if config:
            try:
                self.config = Config(config,
                                     verbosity=self.v, logfile=self.logfile)
            except IOError:
                raise IOError(
                    'Unable to open config file {}!'.format(config))
        else:
            self.vprint(
                1, 'WARNING: no config file given. Not posting to server')
            self.config = None

        if publickey:
            try:
                self.publickey = PublicKey(
                    publickey, verbosity=self.v, logfile=self.logfile)
            except IOError:
                raise IOError(
                    'Unable to load publickey file {}!'.format(publickey))
        else:
            self.vprint(
                1, 'WARNING: no public key given. Not posting to server')
            self.publickey = None

        self.aes = None     #checked in sender, used for the manager_d3s

    def run(self):

        this_start, this_end = self.get_interval(time.time())
        self.vprint(
            1, ('Manager is starting to run at {}' +
                ' with intervals of {}s').format(
                datatime_from_epoch(this_start), self.interval))
        self.running = True

    def stop(self):
        """Stop counting time"""
        self.running = False

    def get_interval(self, start_time):
        """
        Return start and end time for interval, based on given start_time.
        """
        end_time = start_time + self.interval
        return start_time, end_time

    def data_log(self):
        pass

    def handle_air_counts(self, this_start, this_end):

        summation = sum(buffer[0:30])
        checkbyte = (buffer[30]<<8)+buffer[31]
        current_time = int(time.time())
        aq_data_set = []
        while current_time < this_end:
            text = self.port.read(32)
            buffer = [ord(c) for c in text]
            if buffer[0] == 66:
                summation = sum(buffer[0:30])
                checkbyte = (buffer[30]<<8)+buffer[31]
                if summation == checkbyte:
                    current_second_data = []
                    buf = buffer[1:32]
                    current_second_data.append(datetime.datetime.now())
                    for n in range(1,4):
                        current_second_data.append(repr(((buf[(2*n)+1]<<8) + buf[(2*n)+2])))
                    for n in range(1,7):
                        current_second_data.append(repr(((buf[(2*n)+13]<<8) + buf[(2*n)+14])))
                    aq_data_set.append(current_second_data)
        self.data_handler.main(
            self.datalog, this_start, this_end)
    def takedown(self):
        """
        Sends data to the backlog and shuts
        down the manager
        """
        self.data_handler.send_all_to_backlog()

        del(self)

    @classmethod
    def from_argparse(cls):
        parser = argparse.ArgumentParser()
        parser.add_argument('--interval', '-i', type=int, default=None)
        parser.add_argument(
            '--sender-mode', '-m', type=str, default=DEFAULT_SENDER_MODE,
            choices=['udp', 'tcp', 'UDP', 'TCP'])
        parser.add_argument('--verbosity', '-v', type=int, default=None)
        parser.add_argument('--log', '-l', action='store_true', default=False)
        parser.add_argument('--logfile', '-f', type=str, default=None)
        parser.add_argument('--datalog', '-d', default=None)
        parser.add_argument(
            '--datalogflag', '-a', action='store_true', default=False)
        parser.add_argument('--config', '-c', default=None)
        parser.add_argument('--publickey', '-k', default=None)
        parser.add_argument('--hostname', '-s', default=DEFAULT_HOSTNAME)
        parser.add_argument('--port', '-p', type=int, default=None)
        parser.add_argument('--test', '-t', action='store_true', default=False)

        args = parser.parse_args()
        arg_dict = vars(args)
        mgr = Manager_D3S(**arg_dict)

        return mgr

if __name__ == '__main__':
    mgr = Manager_D3S.from_argparse()
    try:
        mgr.run()
    except:
        if mgr.logfile:
            # print exception info to logfile
            with open(mgr.logfile, 'a') as f:
                traceback.print_exc(15, f)
        # regardless, re-raise the error which will print to stderr
        raise
