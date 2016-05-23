# -*- coding: utf-8 -*-
from __future__ import print_function


import time
import argparse
import traceback

from globalvalues import RPI
if RPI:
    import RPi.GPIO as GPIO

from auxiliaries import LED, Config, PublicKey, NetworkStatus
from auxiliaries import datetime_from_epoch, set_verbosity
from sensor import Sensor
from sender import ServerSender

from globalvalues import SIGNAL_PIN, NOISE_PIN
from globalvalues import POWER_LED_PIN, NETWORK_LED_PIN, COUNTS_LED_PIN
from globalvalues import DEFAULT_CONFIG, DEFAULT_PUBLICKEY, DEFAULT_LOGFILE
from globalvalues import DEFAULT_HOSTNAME, DEFAULT_PORT
from globalvalues import DEFAULT_INTERVAL_NORMAL, DEFAULT_INTERVAL_TEST
from globalvalues import ANSI_RESET, ANSI_YEL, ANSI_GR, ANSI_RED

import signal
import sys

import json

#new
data_log = open('data-log')
content = data_log.readlines(0)
data_log.close()
#new
if content[0] is not ["date", "End Time", "Counts per Minute"]:
    f = open('data-log', 'a')
    json.dump(['date' ,'End Time', 'Counts per Minute'], f)
    f.write('\n')
    f.close()

def signal_term_handler(signal, frame):
    print('got SIGTERM')
    #If SIGTERM signal is intercepted, the SystemExit exception routines are ran
    sys.exit(0)

signal.signal(signal.SIGTERM, signal_term_handler)

# this is hacky, but, the {{}} get converted to {} in the first .format() call
#   and then get filled in later
CPM_DISPLAY_TEXT = (
    '{{time}}: {yellow} {{counts}} cts{reset}' +
    ' --- {green}{{cpm:.2f}} +/- {{cpm_err:.2f}} cpm{reset}' +
    ' ({{start_time}} to {{end_time}})').format(
    yellow=ANSI_YEL, reset=ANSI_RESET, green=ANSI_GR)
strf = '%H:%M:%S'


class Manager(object):
    """
    Master object for dosimeter operation.

    Initializes other classes, tracks time intervals, and converts the counts
    from Sensor into a CPM to give to the server.

    time_interval is the interval (in seconds) over for which CPM is
    calculated.
    """

    # Note: keep the __init__() keywords identical to the keywords in argparse,
    #   in order to avoid unpacking them individually.
    # The None's are handled differently, depending on whether test mode.
    def __init__(self,
                 network_LED_pin=NETWORK_LED_PIN,
                 power_LED_pin=POWER_LED_PIN,
                 counts_LED_pin=COUNTS_LED_PIN,
                 signal_pin=SIGNAL_PIN,
                 noise_pin=NOISE_PIN,
                 test=False,
                 interval=None,
                 config=None,
                 publickey=None,
                 hostname=DEFAULT_HOSTNAME,
                 port=DEFAULT_PORT,
                 verbosity=None,
                 log=False,
                 logfile=None,
                 ):

        self.handle_input(log, logfile, verbosity,
                          test, interval, config, publickey)

        # LEDs
        if RPI:
            self.power_LED = LED(power_LED_pin)
            self.network_LED = LED(network_LED_pin)
            self.counts_LED = LED(counts_LED_pin)

            self.power_LED.on()
        else:
            self.power_LED = None
            self.network_LED = None
            self.counts_LED = None

        # other objects
        self.sensor = Sensor(
            counts_LED=self.counts_LED,
            verbosity=self.v,
            logfile=self.logfile)
        self.network_up = NetworkStatus(
            network_led=self.network_LED,
            verbosity=self.v,
            logfile=self.logfile)
        self.sender = ServerSender(
            manager=self,
            verbosity=self.v,
            logfile=self.logfile)

    def handle_input(self,
                     log, logfile, verbosity,
                     test, interval, config, publickey):

        # resolve logging defaults
        if log and logfile is None:
            # use default file if logging is enabled
            logfile = DEFAULT_LOGFILE
        if logfile and not log:
            # enable logging if logfile is specified
            #   (this overrides a log=False input which wouldn't make sense)
            log = True
        if log:
            self.logfile = logfile
        else:
            self.logfile = None

        # set up verbosity
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
        self.test = test
        self.running = False

        # resolve defaults that depend on test mode
        if self.test:
            if interval is None:
                self.vprint(
                    2, "No interval given, using default for TEST MODE")
                interval = DEFAULT_INTERVAL_TEST
        else:
            if interval is None:
                self.vprint(
                    2, "No interval given, using default for NORMAL MODE")
                interval = DEFAULT_INTERVAL_NORMAL
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

    def run(self):
        """
        Start counting time.

        This method does NOT return, so run in a subprocess if you
        want to keep control.

        However, setting self.running = False will stop, as will a
          KeyboardInterrupt.
        """

        this_start, this_end = self.get_interval(time.time())
        self.vprint(
            1, ('Manager is starting to run at {}' +
                ' with intervals of {}s').format(
                datetime_from_epoch(this_start), self.interval))
        self.running = True

        try:
            while self.running:
                self.vprint(3, 'Sleeping at {} until {}'.format(
                    datetime_from_epoch(time.time()),
                    datetime_from_epoch(this_end)))
                try:
                    self.sleep_until(this_end)
                except SleepError:
                    self.vprint(1, 'SleepError: system clock skipped ahead!')
                    # the previous start/end times are meaningless.
                    # There are a couple ways this could be handled.
                    # 1. keep the same start time, but go until time.time()
                    #    - but if there was actually an execution delay,
                    #      the CPM will be too high.
                    # 2. set start time to be time.time() - interval,
                    #    and end time is time.time().
                    #    - but if the system clock was adjusted halfway through
                    #      the interval, the CPM will be too low.
                    # The second one is more acceptable.
                    self.vprint(
                        3, 'former this_start = {}, this_end = {}'.format(
                            datetime_from_epoch(this_start),
                            datetime_from_epoch(this_end)))
                    this_start, this_end = self.get_interval(
                        time.time() - self.interval)

                self.handle_cpm(this_start, this_end)
                this_start, this_end = self.get_interval(this_end)
        except KeyboardInterrupt:
            self.vprint(1, '\nKeyboardInterrupt: stopping Manager run')
            self.stop()
            self.takedown()
        except SystemExit:
            self.vprint(1, '\nSystemExit: taking down Manager')
            self.stop()
            self.takedown()

    def stop(self):
        """Stop counting time."""
        self.running = False

    def sleep_until(self, end_time):
        """
        Sleep until the given timestamp.

        Input:
          end_time: number of seconds since epoch, e.g. time.time()
        """

        sleeptime = end_time - time.time()
        self.vprint(3, 'Sleeping for {} seconds'.format(sleeptime))
        if sleeptime < 0:
            # this shouldn't happen now that SleepError is raised and handled
            raise RuntimeError
        time.sleep(sleeptime)
        now = time.time()
        self.vprint(
            2, 'sleep_until offset is {} seconds'.format(now - end_time))
        # normally this offset is < 0.1 s
        # although a reboot normally produces an offset of 9.5 s
        #   on the first cycle
        if now - end_time > 10 or now < end_time:
            # raspberry pi clock reset during this interval
            # normally the first half of the condition triggers it.
            raise SleepError

    def get_interval(self, start_time):
        """
        Return start and end time for interval, based on given start_time.
        """
        end_time = start_time + self.interval
        return start_time, end_time

    def handle_cpm(self, this_start, this_end):
        """Get CPM from sensor, display text, send to server."""

        cpm, cpm_err = self.sensor.get_cpm(this_start, this_end)
        counts = int(round(cpm * self.interval / 60))

        start_text = datetime_from_epoch(this_start).strftime(strf)
        end_text = datetime_from_epoch(this_end).strftime(strf)

        self.vprint(1, CPM_DISPLAY_TEXT.format(
            time=datetime_from_epoch(time.time()),
            counts=counts,
            cpm=cpm,
            cpm_err=cpm_err,
            start_time=start_text,
            end_time=end_text,
        ))
        if self.test:
            self.vprint(
                1, ANSI_RED + " * Test mode, not sending to server * " +
                ANSI_RESET)
        elif not self.config:
            self.vprint(1, "Missing config file, not sending to server")
        elif not self.publickey:
            self.vprint(1, "Missing public key, not sending to server")
        elif not self.network_up:
            self.vprint(1, "Network down, not sending to server")
        else:
            self.sender.send_cpm(cpm, cpm_err)
            f = open('data-log', 'a')
            json.dump([time.strftime("%m/%d/%Y"), end_text, cpm], f)
            f.write('\n')
            f.close()
            
    def takedown(self):
        """Delete self and child objects and clean up GPIO nicely."""

        # sensor
        self.sensor.cleanup()
        del(self.sensor)

        # network
        self.network_up.cleanup()
        del(self.network_up)

        # power LED
        self.power_LED.off()
        GPIO.cleanup()

        # self. can I even do this?
        del(self)

    @classmethod
    def from_argparse(cls):
        """
        Initialize a Manager instance using arguments from the command line.

        For usage:
        python manager.py -h
        """

        # Note: keep the keywords identical to the keywords in __init__(),
        #   to avoid individual handling of arguments.
        # The arguments with default=None depend on test state.
        #   They are handled in __init__()
        # Also, LED pin numbers could be added here if you want.

        parser = argparse.ArgumentParser(
            description="Manager for the DoseNet radiation detector")
        # test mode
        parser.add_argument(
            '--test', '-t', action='store_true', default=False,
            help='Start in test mode (no config, 30s intervals)')
        # interval: default depends on whether test mode is enabled
        parser.add_argument(
            '--interval', '-i', type=int, default=None,
            help=('Interval of CPM measurement, in seconds' +
                  ' (default 300 for normal mode)'))
        # verbosity
        parser.add_argument(
            '--verbosity', '-v', type=int, default=None,
            help='Verbosity level (0 to 3) (default 1)')
        parser.add_argument(
            '--log', '-l', action='store_true', default=False,
            help='Enable file logging of all verbose text (default off)')
        parser.add_argument(
            '--logfile', '-f', type=str, default=None,
            help='Specify file for logging (default {})'.format(
                DEFAULT_LOGFILE))
        # config file and public key
        parser.add_argument(
            '--config', '-c', default=None,
            help='Specify a config file (default {})'.format(DEFAULT_CONFIG))
        parser.add_argument(
            '--publickey', '-k', default=None,
            help='Specify a publickey file (default {})'.format(
                DEFAULT_PUBLICKEY))
        # server address and port
        parser.add_argument(
            '--hostname', '-s', default=DEFAULT_HOSTNAME,
            help='Specify a server hostname (default {})'.format(
                DEFAULT_HOSTNAME))
        parser.add_argument(
            '--port', '-p', type=int, default=DEFAULT_PORT,
            help='Specify a port for the server (default {})'.format(
                DEFAULT_PORT))

        args = parser.parse_args()
        arg_dict = vars(args)
        mgr = Manager(**arg_dict)

        return mgr


class SleepError(Exception):
    pass


if __name__ == '__main__':
    mgr = Manager.from_argparse()
    try:
        mgr.run()
    except:
        if mgr.logfile:
            # print exception info to logfile
            with open(mgr.logfile, 'a') as f:
                traceback.print_exc(15, f)
        # regardless, re-raise the error which will print to stderr
        raise
