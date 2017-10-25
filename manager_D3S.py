import time
import traceback
import argparse
import kromek
import numpy as np
import signal
import sys
import os
from Crypto.Cipher import AES
from collections import deque

try:
    import RPi.GPIO as GPIO
    RPI = True
except ImportError:
    print('Not connected to a Raspberry Pi, try again')
    RPI = False

from auxiliaries import Config, PublicKey, set_verbosity
from auxiliaries import datetime_from_epoch, set_verbosity
from sender import ServerSender
from data_handler_d3s import Data_Handler_D3S

from auxiliaries import LED
from globalvalues import D3S_LED_PIN
from globalvalues import D3S_LED_BLINK_PERIOD_INITIAL, D3S_LED_BLINK_PERIOD_DEVICE_FOUND

from globalvalues import DEFAULT_CONFIG, DEFAULT_PUBLICKEY, DEFAULT_AESKEY
from globalvalues import DEFAULT_CALIBRATIONLOG_D3S, DEFAULT_LOGFILE_D3S
from globalvalues import DEFAULT_CALIBRATIONLOG_TIME
from globalvalues import DEFAULT_HOSTNAME, DEFAULT_UDP_PORT, DEFAULT_TCP_PORT
from globalvalues import DEFAULT_SENDER_MODE
from globalvalues import DEFAULT_DATALOG_D3S
from globalvalues import DEFAULT_INTERVAL_NORMAL_D3S
from globalvalues import DEFAULT_D3STEST_TIME


def signal_term_handler(signal, frame):
    # If SIGTERM signal is intercepted, the SystemExit exception routines
    #   get run
    sys.exit(0)

signal.signal(signal.SIGTERM, signal_term_handler)


class Manager_D3S(object):
    """
    Master object for D3S device operation.
    Prints out spectra for every interval, stores each spectra, and
    sums the spectra together.
    Interval is in seconds with the default being 30 seconds.
    """

    def __init__(self,
                 interval=None,
                 count=0,
                 transport='any',
                 device='all',
                 log_bytes=False,
                 verbosity=None,
                 datalog=None,
                 datalogflag=False,
                 calibrationlog=None,
                 calibrationlogflag=False,
                 calibrationlogtime=None,
                 test=None,
                 config=None,
                 publickey=None,
                 aeskey=None,
                 hostname=DEFAULT_HOSTNAME,
                 port=None,
                 sender_mode=DEFAULT_SENDER_MODE,
                 logfile=None,
                 log=False,
                 running=False,
                 d3s_LED_pin=D3S_LED_PIN,
                 d3s_light_switch=False,
                 d3s_LED_blink_period_1=D3S_LED_BLINK_PERIOD_INITIAL,
                 d3s_LED_blink_period_2=D3S_LED_BLINK_PERIOD_DEVICE_FOUND,
                 d3s_LED_blink=True,
                 signal_test_time=DEFAULT_D3STEST_TIME,
                 signal_test_loop=True,
                 signal_test_connection=False,
                 signal_test_attempts=0,
                 ):

        self.running = running

        self.total = None
        self.lst = None
        self.create_structures = True

        self.interval = interval
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

        self.datalog = datalog
        self.datalogflag = datalogflag

        self.a_flag()
        self.d_flag()
        self.make_data_log(self.datalog)

        self.test = test

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
        else:
            self.d3s_LED.on()

        self.handle_input(
            log, logfile, verbosity, interval, config, publickey, aeskey)

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
        # DEFAULT_UDP_PORT and DEFAULT_TCP_PORT are assigned in sender

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

    def a_flag(self):
        """
        Checks if the -a from_argparse is called.
        If it is called, sets the path of the data-log to
        DEFAULT_DATALOG_D3S.
        """
        if self.datalogflag:
            self.datalog = DEFAULT_DATALOG_D3S

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
                     config, publickey, aeskey):
        """
        Sets up logging, verbosity, interval, config, and publickey
        """

        # resolve logging defaults
        if log and logfile is None:
            # use default file if logging is enabled
            logfile = DEFAULT_LOGFILE_D3S
        if logfile and not log:
            # enable logging if logfile is specified
            #   (this overrides a log=False input which wouldn't make sense)
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
        self.running = True

        if interval is None:
            self.vprint(
                2, "No interval given, using interval at 30 seconds")
            interval = DEFAULT_INTERVAL_NORMAL_D3S
        if config is None:
            self.vprint(2, "No config file given, " +
                        "attempting to use default config path")
            config = DEFAULT_CONFIG
        if publickey is None:
            self.vprint(2, "No publickey file given, " +
                        "attempting to use default publickey path")
            publickey = DEFAULT_PUBLICKEY
        if aeskey is None:
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

    def run(self):
        """
        Main method. Currently also stores and sum the spectra as well.
        Current way to stop is only using a keyboard interrupt.
        """
        if self.transport == 'any':
            devs = kromek.discover()
        else:
            devs = kromek.discover(self.transport)

        if len(devs) <= 0:
            print("No D3S connected, exiting manager now")
            self.d3s_LED.stop_blink()
            GPIO.cleanup()
            return
        else:
            print 'Discovered %s' % devs
            print("D3S device found, checking for data now")
            self.d3s_LED.start_blink(interval=self.d3s_LED_blink_period_2)
        filtered = []

        for dev in devs:
            if self.device == 'all' or dev[0] in self.device:
                filtered.append(dev)

        devs = filtered
        if len(devs) <= 0:
            print("No D3S connected, exiting manager now")
            self.d3s_LED.stop_blink()
            GPIO.cleanup()
            return

        # Checks if the RaspberryPi is getting data from the D3S and turns on
        # the red LED if it is. If a D3S is connected but no data is being recieved,
        # it tries a couple times then reboots the RaspberryPi.
        try:
            while self.signal_test_attempts < 3 and self.signal_test_connection == False:
                test_time = time.time() + self.signal_test_time + 5
                while time.time() < test_time and self.signal_test_loop:
                    with kromek.Controller(devs, self.signal_test_time) as controller:
                        for reading in controller.read():
                            if sum(reading[4]) != 0:
                                self.d3s_light_switch = True
                                self.signal_test_loop = False
                                break
                            else:
                                self.signal_test_loop = False
                                break
                if self.d3s_light_switch:
                    self.signal_test_connection = True
                else:
                    self.signal_test_attempts += 1
                    self.signal_test_loop = True
                    print("Connection to D3S not found, trying another {} times".format(3 - self.signal_test_attempts))
            if not self.signal_test_connection:
                print("No data from D3S found, restarting now")
                os.system('sudo reboot')
        except KeyboardInterrupt:
            self.vprint(1, '\nKeyboardInterrupt: stopping Manager run')
            self.takedown()
        except SystemExit:
            self.vprint(1, '\nSystemExit: taking down Manager')
            self.takedown()

        if self.d3s_light_switch:
            self.d3s_LED.stop_blink()
            print("D3S data connection found, continuing with normal data collection")
            self.d3s_LED.on()

        done_devices = set()
        try:
            while self.running:
                with kromek.Controller(devs, self.interval) as controller:
                    for reading in controller.read():
                        if self.create_structures:
                            self.total = np.array(reading[4])
                            self.lst = np.array([reading[4]])
                            self.create_structures = False
                        else:
                            self.total += np.array(reading[4])
                            self.lst = np.concatenate(
                                (self.lst, [np.array(reading[4])]))
                        serial = reading[0]
                        dev_count = reading[1]
                        if serial not in done_devices:
                            this_start, this_end = self.get_interval(
                                time.time() - self.interval)

                            self.handle_spectra(
                                this_start, this_end, reading[4])

                        if dev_count >= self.count > 0:
                            done_devices.add(serial)
                            controller.stop_collector(serial)
                        if len(done_devices) >= len(devs):
                            break
        except KeyboardInterrupt:
            self.vprint(1, '\nKeyboardInterrupt: stopping Manager run')
            self.takedown()
        except SystemExit:
            self.vprint(1, '\nSystemExit: taking down Manager')
            self.takedown()

    def get_interval(self, start_time):
        """
        Return start and end time for interval, based on given start_time.
        """
        end_time = start_time + self.interval
        return start_time, end_time

    def data_log(self, file, **kwargs):
        """
        Writes spectra to data-log.
        """
        spectra = kwargs.get('spectra')
        if self.datalogflag:
            with open(file, 'a') as f:
                f.write('{0}, '.format(spectra))
                self.vprint(
                    2, 'Writing spectra to data log at {}'.format(file))

    def calibration_log(self, file, spectra):
        """
        Writes spectra to calibration-log.
        """
        if self.calibrationlogflag:
            with open(file, 'a') as f:
                f.write('{0}, '.format(spectra))
                self.vprint(
                    2, 'Writing spectra to calibration log at {}'.format(file))
            self.c_timer += self.interval
            if self.c_timer >= self.calibrationlogtime:
                self.vprint(1, 'Calibration Complete')
                self.takedown()

    def handle_spectra(self, this_start, this_end, spectra):
        """
        Get spectra from sensor, display text, send to server.
        """
        self.data_handler.main(
            self.datalog, self.calibrationlog, spectra, this_start, this_end)

    def takedown(self):
        """
        Sets self.running to False and deletes self. Also turns off LED
        """
        self.running = False
        self.data_handler.send_all_to_backlog()

        try:
            self.d3s_LED.off()
        except AttributeError:
            pass

        try:
            GPIO.cleanup()
        except NameError:
            pass

        del(self)

    @classmethod
    def from_argparse(cls):
        parser = argparse.ArgumentParser()
        parser.add_argument('--hostname', '-s', default=DEFAULT_HOSTNAME)
        parser.add_argument('--port', '-p', type=int, default=None)
        parser.add_argument(
            '--sender-mode', '-m', type=str, default=DEFAULT_SENDER_MODE,
            choices=['udp', 'tcp', 'UDP', 'TCP'])
        parser.add_argument('--config', '-c', default=None)
        parser.add_argument('--datalog', '-d', default=None)
        parser.add_argument(
            '--datalogflag', '-a', action='store_true', default=False)
        parser.add_argument('--publickey', '-k', default=None)
        parser.add_argument('--verbosity', '-v', type=int, default=None)
        parser.add_argument('--test', '-t', action='store_true', default=False)
        parser.add_argument('--transport', '-n', default='any')
        parser.add_argument('--interval', '-i', type=int, default=None)
        parser.add_argument('--count', '-0', dest='count', default=0)
        parser.add_argument('--device', '-e', dest='device', default='all')
        parser.add_argument(
            '--log-bytes', '-b', dest='log_bytes', default=False,
            action='store_true')
        parser.add_argument('--log', '-l', action='store_true', default=False)
        parser.add_argument('--logfile', '-f', type=str, default=None)
        parser.add_argument('--calibrationlogtime', '-x', type=int, default=None)
        parser.add_argument('--calibrationlog', '-y', default=None)
        parser.add_argument(
            '--calibrationlogflag', '-z', action='store_true', default=False)

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