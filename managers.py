from __future__ import print_function

import time
import argparse
import traceback
import signal
import sys
import os
import subprocess
import socket

from globalvalues import RPI
if RPI:
    import RPi.GPIO as GPIO

from auxiliaries import LED, Config, PublicKey
from auxiliaries import datetime_from_epoch, set_verbosity
from sensor import Sensor
from sender import ServerSender
from data_handler import Data_Handler
from data_handler_d3s import Data_Handler_D3S
from data_handler_aq import Data_Handler_AQ

from globalvalues import SIGNAL_PIN, NOISE_PIN, NETWORK_LED_BLINK_PERIOD_S
from globalvalues import NETWORK_LED_PIN, COUNTS_LED_PIN
from globalvalues import D3S_LED_PIN
from globalvalues import D3S_LED_BLINK_PERIOD_INITIAL, D3S_LED_BLINK_PERIOD_DEVICE_FOUND

from globalvalues import DEFAULT_CONFIG, DEFAULT_PUBLICKEY, DEFAULT_LOGFILE
from globalvalues import DEFAULT_HOSTNAME, DEFAULT_UDP_PORT, DEFAULT_TCP_PORT
from globalvalues import DEFAULT_SENDER_MODE
from globalvalues import DEFAULT_CALIBRATIONLOG_D3S, DEFAULT_LOGFILE_D3S
from globalvalues import DEFAULT_CALIBRATIONLOG_TIME
from globalvalues import DEFAULT_HOSTNAME, DEFAULT_UDP_PORT, DEFAULT_TCP_PORT
from globalvalues import DEFAULT_INTERVAL_NORMAL, DEFAULT_INTERVAL_TEST
from globalvalues import DEFAULT_INTERVAL_NORMAL_D3S, DEFAULT_INTERVAL_TEST_D3S, DEFAULT_D3STEST_TIME
from globalvalues import DEFAULT_INTERVAL_NORMAL_AQ, DEFAULT_INTERVAL_TEST_AQ
from globalvalues import DEFAULT_DATALOG, DEFAULT_DATALOG_D3S, DEFAULT_DATALOG_AQ
from globalvalues import DEFAULT_AQ_PORT, AQ_VARIABLES
from globalvalues import DEFAULT_DATALOG_AQ
from globalvalues import DEFAULT_PROTOCOL
from globalvalues import REBOOT_SCRIPT, GIT_DIRECTORY

def signal_term_handler(signal, frame):
    # If SIGTERM signal is intercepted, the SystemExit exception routines
    #   get run
    sys.exit(0)

signal.signal(signal.SIGTERM, signal_term_handler)

class Manager(object):
    """
    Main Manager class that contains the general functions for any
    of the connected detectors or sensors.

    The specific functions are handled in the sub classes below this class.
    """
    def __init__(self,
                 interval=None,
                 config=None,
                 publickey=None,
                 hostname=DEFAULT_HOSTNAME,
                 port=None,
                 test=None,
                 verbosity=None,
                 log=False,
                 logfile=None,
                 datalog=None,
                 datalogflag=False,
                 sender_mode=DEFAULT_SENDER_MODE,
                 aeskey=None,
                 sensor_type=None,
                 ):
        self.sensor_type = sensor_type

        self.datalog = datalog
        self.datalogflag = datalogflag

        self.a_flag()
        self.d_flag()
        self.make_data_log(self.datalog)

        self.handle_input(log, logfile, verbosity,
                          test, interval, config, publickey, aeskey)

        self.test = test

    def a_flag(self):
        """
        Checks if the -a from_argparse is called.

        If it is called, sets the path of the data-log to
        DEFAULT_DATALOG.
        """
        if self.datalogflag and self.sensor_type == 1:
            self.datalog = DEFAULT_DATALOG
        if self.datalogflag and self.sensor_type == 2:
            self.datalog = DEFAULT_DATALOG_D3S
        if self.datalogflag and self.sensor_type == 3:
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

    def handle_input(self, log, logfile, verbosity,
                         interval, config, publickey, aeskey):

        if log and self.sensor_type == None:
            self.vprint(1,
                "No sensor running, try executing one of the subclasses to get a proper setup.")
            self.takedown()
        if log and self.sensor_type == 1:
            #If the sensor type is a pocket geiger use the pocket geiger log file
            logfile = DEFAULT_LOGFILE

        if log and self.sensor_type == 2:
            #If the sensor type is a D3S use the D3S log file
            logfile = DEFAULT_LOGFILE_D3S

        if log and self.sensor_type == 3:
            #If the sensor type is an air quality sensor use the air quality log file
            logfile = DEFAULT_LOGFILE_AQ

        if log:
            self.logfile = logfile
        else:
            self.logfile = None

        if verbosity is None:
            if test:
                verbosity = 2
            else:
                verbosity = 1
        self.v = verbosity
        set_verbosity(self, logfile=logfile)

        if log:
            self.vprint(1, '')
            self.vprint(1, 'Writing to logfile at {}'.format(self.logfile))
        self.running = True

        if self.test and self.sensor_type == 1:
            if interval is None:
                self.vprint(
                    2, "No interval given, using default for TEST MODE")
                interval = DEFAULT_INTERVAL_TEST
        if self.test and self.sensor_type == 2:
            if interval is None:
                self.vprint(
                    2, "No interval given, using default for D3S TEST MODE")
                interval = DEFAULT_INTERVAL_TEST_D3S
        if self.test and self.sensor_type == 3:
            if interval is None:
                self.vprint(
                    2, "No interval given, using default for AQ TEST MODE")
                interval = DEFAULT_INTERVAL_TEST_AQ

        if interval is None and sensor_type == 1:
            self.vprint(
                2, "No interval given, using interval at 5 minutes")
            interval = DEFAULT_INTERVAL_NORMAL
        if interval is None and sensor_type == 2:
            self.vprint(
                2, "No interval given, using interval at 5 minutes")
            interval = DEFAULT_INTERVAL_NORMAL_D3S
        if interval is None and sensor_type == 3:
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
        if aeskey is None and sensor_type == 2:
            #Only set the AES key when the D3S is being used
            self.vprint(2, "No AES key file given, " +
                        "attempting to use default AES key path")
            aeskey = DEFAULT_AESKEY

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

        if aeskey:
            try:
                with open(aeskey, 'r') as aesfile:
                    key = aesfile.read()
                    self.aes = AES.new(key, mode=AES.MODE_ECB)
            except IOError:
                raise IOError('Unable to load AES key file {}!'.format(
                    aeskey))
        else:
            self.vprint(
                1, 'WARNING: no AES key given. Not posting to server')
            self.aes = None

    def get_interval(self, start_time):
        """
        Return start and end time for interval, based on given start_time.
        """
        end_time = start_time + self.interval
        return start_time, end_time

    def takedown(self):
        """
        Shuts down any sensors or lights and runs unique procedures for
        individual sensors. Then cleans up GPiO for clean restart procedure and
        deletes itself.
        """

        #Unique shutdown procedure for Pocket Geiger
        if self.sensor_type == 1:
            self.sensor.cleanup()
            del(self.sensor)

        #Unique shutdown procedure for D3S
        if self.sensor_type == 2:
            self.running = False
            try:
                self.d3s_LED.off()
            except AttributeError:
                pass

        try:
            GPIO.cleanup()
        except NameError:
            pass

        self.data_handler.send_all_to_backlog()

        del(self)

    @classmethod
    def from_argparse(cls):
        parser = argparser.ArgumentParser()
        parser.add_argument(
            '--interval', '-i', type=int, default=None,
            help=('Interval of CPM measurement, in seconds' +
                  ' (default 300 for normal mode)'))
        parser.add_argument(
            '--config', '-c', default=None,
            help='Specify a config file (default {})'.format(DEFAULT_CONFIG))
        parser.add_argument(
            '--publickey', '-k', default=None,
            help='Specify a publickey file (default {})'.format(
                DEFAULT_PUBLICKEY))
        parser.add_argument(
            '--hostname', '-h', default=DEFAULT_HOSTNAME,
            help='Specify a server hostname (default {})'.format(
                DEFAULT_HOSTNAME))
        parser.add_argument(
            '--port', '-p', type=int, default=None,
            help='Specify a port for the server ' +
            '(default {} for UDP, {} for TCP)'.format(
                DEFAULT_UDP_PORT, DEFAULT_TCP_PORT))
        parser.add_argument(
            '--test', '-t', action='store_true', default=False,
            help='Start in test mode (no config, 30s intervals)')
        parser.add_argument(
            '--verbosity', '-v', type=int, default=None,
            help='Verbosity level (0 to 3) (default 1)')
        parser.add_argument(
            '--log', '-g', action='store_true', default=False,
            help='Enable file logging of all verbose text (default off)')
        parser.add_argument(
            '--datalogflag', '-q', action='store_true', default=False,
            help='Enable logging local data (default off)')
        parser.add_argument(
            '--sender-mode', '-m', type=str, default=DEFAULT_SENDER_MODE,
            choices=['udp', 'tcp', 'UDP', 'TCP'],
            help='The network protocol used in sending data ' +
            '(default {})'.format(DEFAULT_SENDER_MODE))
        args = parser.parse_args()
        super_dict = vars(args)

        return super_dict

class Manager_Pocket(Manager):
    """
    The subclass that uses the main Manager class and initializes the
    pocket geiger sensor.
    """
    def __init__(self,
                 counts_LED_pin=COUNTS_LED_PIN,
                 network_LED_pin=NETWORK_LED_PIN,
                 noise_pin=NOISE_PIN,
                 signal_pin=SIGNAL_PIN,
                 protocol=DEFAULT_PROTOCOL,
                 **kwargs,
                 ):

        super().__init__(sensor_type=1, **kwargs)

        if RPI:
            self.counts_LED = LED(counts_LED_pin)
            self.network_LED = LED(network_LED_pin)
        else:
            self.counts_LED = None
            self.network_LED = None

        self.sensor = Sensor(
            counts_LED=self.counts_LED,
            verbosity=self.v,
            logfile=self.logfile)
        self.data_handler = Data_Handler(
            manager=self,
            verbosity=self.v,
            logfile=self.logfile,
            network_led=self.network_LED)
        self.sender = ServerSender(
            manager=self,
            mode=sender_mode,
            port=port,
            verbosity=self.v,
            logfile=self.logfile)

        self.init_log()
        self.branch = ''

        self.data_handler.backlog_to_queue()

    def init_log(self):
        """
        Post log message to server regarding Manager startup.
        """

        # set working directory
        cwd = os.getcwd()
        os.chdir(GIT_DIRECTORY)

        branch = subprocess.check_output(
            ['git', 'rev-parse', '--abbrev-ref', 'HEAD']).rstrip()
        self.vprint(3, 'Found git branch: {}'.format(branch))
        commit = subprocess.check_output(
            ['git', 'rev-parse', '--short', 'HEAD']).rstrip()
        self.vprint(3, 'Found commit: {}'.format(commit))

        os.chdir(cwd)

        msg_code = BOOT_LOG_CODE
        msg_text = 'Booting on {} at {}'.format(branch, commit)
        self.vprint(1, 'Sending log message: [{}] {}'.format(
            msg_code, msg_text))
        try:
            self.sender.send_log(msg_code, msg_text)
        except (socket.gaierror, socket.error, socket.timeout):
            self.vprint(1, 'Failed to send log message, network error')
            if self.network_LED:
                self.network_LED.start_blink(
                    interval=NETWORK_LED_BLINK_PERIOD_S)
        else:
            self.vprint(2, 'Success sending log message')
            if self.network_LED:
                if self.network_LED.blinker:
                    self.network_LED.stop_blink()
                self.network_LED.on()

    @classmethod
    def from_argparse(cls):
        super_dict = super().from_argparse()
        parser = argparse.ArgumentParser()
        parser.add_argument(
            '--counts_LED_pin', '-o', default=COUNTS_LED_PIN,
            help='Specify which pin the counts LED is connected to ' +
            '(default {})'.format(COUNTS_LED_PIN))
        parser.add_argument(
            '--network_LED_pin', '-e', default=NETWORK_LED_PIN,
            help='Specify which pin the network LED is connected to ' +
            '(default {})'.format(NETWORK_LED_PIN))
        parser.add_argument(
            '--noise_pin', '-n', default=NOISE_PIN,
            help='Specify which pin to the noise reader is connected to ' +
            '(default {})'.format(NOISE_PIN))
        parser.add_argument(
            '--signal_pin', '-s', default=SIGNAL_PIN,
            help='Specify which pin the signal is coming in from ' +
            '(default {})'.format(SIGNAL_PIN))
        parser.add_argument(
            '--protocol', '-r', default=DEFAULT_PROTOCOL,
            help='Specify what communication protocol is to be used ' +
            '(default {})'.format(DEFAULT_PROTOCOL))
        #Put these last in each subclass argparse
        #These specify the default datalog/logfile for which
        #the help is unique to each sensor
        parser.add_argument(
            '--logfile', '-l', type=str, default=None,
            help='Specify file for logging (default {})'.format(
                DEFAULT_LOGFILE))
        parser.add_argument(
            '--datalog', '-d', default=None,
            help='Specify a path for the datalog (default {})'.format(
                DEFAULT_DATALOG))
        args = parser.parse_args()
        arg_dict = vars(args)
        arg_dict.update(super_dict)
        mgr = Manager_Pocket(**arg_dict)

        return mgr

class Manager_D3S(Manager):
    """
    The subclass that uses the main Manager class and initializes the D3S.
    """
    def __init__(self,
                 calibrationlog=None,
                 calibrationlogflag=False,
                 calibrationlogtime=None,
                 count=0,
                 d3s_LED_pin=D3S_LED_PIN,
                 d3s_LED_blink=True,
                 d3s_LED_blink_period_1=D3S_LED_BLINK_PERIOD_INITIAL,
                 d3s_LED_blink_period_2=D3S_LED_BLINK_PERIOD_DEVICE_FOUND,
                 d3s_light_switch=False,
                 device='all',
                 log_bytes=False,
                 running=False,
                 signal_test_attempts=0,
                 signal_test_connection=False,
                 signal_test_loop=True,
                 signal_test_time=DEFAULT_D3STEST_TIME,
                 transport='any',
                 **kwargs,
                 ):

        super().__init__(sensor_type=2, **kwargs)

        self.running = running

        self.total = None
        self.lst = None
        self.create_structures = True

        self.count = count

        self.transport = transport
        self.device = device
        self.log_bytes = log_bytes

        self.calibrationlog = calibrationlog
        self.calibrationlogflag = calibrationlogflag
        self.c_timer = 0
        self.calibrationlogtime = calibrationlogtime

        self.z_flag()
        self.y_flag()
        self.x_flag()
        self.make_calibration_log(self.calibrationlog)

        self.signal_test_time = signal_test_time
        self.signal_test_loop = signal_test_loop
        self.signal_test_connection = signal_test_connection
        self.signal_test_attempts = signal_test_attempts

        self.d3s_LED = LED(d3s_LED_pin)
        self.d3s_light_switch = d3s_light_switch
        self.d3s_LED_blink_period_1 = d3s_LED_blink_period_1
        self.d3s_LED_blink_period_2 = d3s_LED_blink_period_2
        self.d3s_LED_blink = d3s_LED_blink

        if d3s_LED_blink:
            print("Attempting to connect to D3S now")
            self.d3s_LED.start_blink(interval=self.d3s_LED_blink_period_1)
        if d3s_light_switch:
            self.d3s_LED.on()

        self.data_handler = Data_Handler_D3S(
            manager=self,
            verbosity=self.v,
            logfile=self.logfile,)
        self.sender = ServerSender(
            manager=self,
            mode=sender_mode,
            port=port,
            verbosity=self.v,
            logfile=self.logfile,)

        self.data_handler.backlog_to_queue()

    def z_flag(self):
        """
        Checks if the -z from_argparse is called.
        If it is called, sets the path of the calibration-log to
        DEFAULT_CALIBRATIONLOG_D3S.
        """
        if self.calibrationlogflag:
            self.calibrationlog = DEFAULT_CALIBRATIONLOG_D3S

    def y_flag(self):
        """
        Checks if the -y from_argparse is called.
        If it is called, sets calibrationlogflag to True.
        Also sets calibrationlogtime to DEFAULT_CALIBRATIONLOG_TIME.
        """
        if self.calibrationlog:
            self.calibrationlogflag = True
            self.calibrationlogtime = DEFAULT_CALIBRATIONLOG_TIME

    def x_flag(self):
        """
        Checks if -x is called.
        If it is called, sets calibrationlogflag to True.
        Also sets calibrationlog to DEFAULT_CALIBRATIONLOG_D3S.
        """
        if self.calibrationlogtime and (
                self.calibrationlogtime != DEFAULT_CALIBRATIONLOG_TIME):
            self.calibrationlog = DEFAULT_CALIBRATIONLOG_D3S
            self.calibrationlogflag = True

    def make_calibration_log(self, file):
        if self.calibrationlogflag:
            with open(file, 'a') as f:
                pass

    @classmethod
    def from_argparse(cls):
        super_dict = super().from_argparse()
        parser = argparse.ArgumentParser
        parser.add_argument(
            '--calibrationlog', '-y', default=None,
            help='Specify the calibration log for the D3S ' +
            '(default {})'.format(DEFAULT_CALIBRATIONLOG_D3S))
        parser.add_argument(
            '--calibrationlogflag', '-z', action='store_true', default=False,
            help='Specify whether the D3S should store a calibration log ' +
            '(default False)')
        parser.add_argument(
            '--calibrationlogtime', '-x', type=int, default=None,
            help='Specify the amount of time the D3S should take to calibrate ' +
            '(default 10 minutes)')
        parser.add_argument('--count', '-0', dest='count', default=0)
        parser.add_argument(
            '--d3s_LED_pin', '-3', default=D3S_LED_PIN,
            help='Specify which pin the D3S LED is connected to ' +
            '(default {})'.format(D3S_LED_PIN))
        parser.add_argument(
            '--d3s_LED_blink', '-b', default=True,
            help='Decides whether to blink the d3s LED when looking for the device ' +
            '(default On)')
        parser.add_argument(
            '--d3s_LED_blink_period_1', '-1', default=D3S_LED_BLINK_PERIOD_INITIAL,
            help='Specify the frequency that the D3S LED blinks ' +
            'when looking for the device (default {})'.format(D3S_LED_BLINK_PERIOD_INITIAL))
        parser.add_argument(
            '--d3s_LED_blink_period_2', '-2', default=D3S_LED_BLINK_PERIOD_DEVICE_FOUND,
            help='Specify the frequency that the D3S LED blinks when a device is ' +
            'found \nand is now waiting to recieve initial data from the device ' +
            '(default {})'.format(D3S_LED_BLINK_PERIOD_DEVICE_FOUND))
        parser.add_argument(
            '--d3s_light_switch', '-s', default=False,
            help='Specify whether the D3S LED should start on or not ' +
            '(default Off)')
        parser.add_argument('--device', '-e', dest='device', default='all')
        parser.add_argument(
            '--log-bytes', '-y', dest='log_bytes', default=False,
            action='store_true')
        parser.add_argument('--transport', '-n', default='any')
        #Put these last in each subclass argparse
        #These specify the default datalog/logfile for which
        #the help is unique to each sensor
        parser.add_argument(
            '--logfile', '-l', type=str, default=None,
            help='Specify file for logging (default {})'.format(
                DEFAULT_LOGFILE_D3S))
        parser.add_argument(
            '--datalog', '-d', default=None,
            help='Specify a path for the datalog (default {})'.format(
                DEFAULT_DATALOG_D3S))
        args = parser.parse_args()
        arg_dict = vars(args)
        arg_dict.update(super_dict)
        mgr = Manager_D3S(**arg_dict)

        return mgr

class Manager_AQ(Manager):
    """
    The subclass that uses the main Manager class and initializes the
    Air Quality sensor.
    """
    def __init__(self,
                 AQ_port=DEFAULT_AQ_PORT,
                 variables=AQ_VARIABLES,
                 **kwargs,
                 ):

        super().__init__(sensor_type=3, **kwargs):

        self.AQ_port = AQ_port

        self.variable = variables

        self.data_handler = Data_Handler_AQ(
            manager=self,
            verbosity=self.v,
            logfile=self.logfile,
            variables=self.variables)
        self.sender = ServerSender(
            manager=self,
            mode=sender_mode,
            port=port,
            verbosity=self.v,
            logfile=self.logfile)

        self.data_handler.backlog_to_queue()

    @classmethod
    def from_argparse(cls):
        super_dict = super().from_argparse()
        parser = argparse.ArgumentParser()
        parser.add_argument(
            '--AQ_port', '-a', default=DEFAULT_AQ_PORT,
            help='Specify which port the Air Quality sensor is sending ' +
            'data through \n[note, this is a Serial Port so be sure to use ' +
            'Serial port notation] (default {})'.format(DEFAULT_AQ_PORT))
        #Put these last in each subclass argparse
        #These specify the default datalog/logfile for which
        #the help is unique to each sensor
        parser.add_argument(
            '--logfile', '-l', type=str, default=None,
            help='Specify file for logging (default {})'.format(
                DEFAULT_LOGFILE_AQ))
        parser.add_argument(
            '--datalog', '-d', default=None,
            help='Specify a path for the datalog (default {})'.format(
                DEFAULT_DATALOG_AQ))
        args = parser.parse_args()
        arg_dict = vars(args)
        arg_dict.update(super_dict)
        mgr = Manager_AQ(**arg_dict)

        return mgr
