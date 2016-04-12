# -*- coding: utf-8 -*-
from __future__ import print_function

try:
    import RPi.GPIO as GPIO
    RPI = True
except ImportError:
    print('Not on a Raspberry Pi, proceeding anyway')
    RPI = False

import time
import argparse

from auxiliaries import LED, Config, PublicKey, NetworkStatus
from auxiliaries import datetime_from_epoch
from sensor import Sensor
from sender import ServerSender

# SIG >> float (~3.3V) --> 0.69V --> EXP charge back to float (~3.3V)
# NS  >> ~0V (GPIO.LOW) --> 3.3V (GPIO.HIGH) RPi rail

# Standard pin numbers (Broadcom, a.k.a. what's labeled on the pi hat):
SIGNAL_PIN = 17
NOISE_PIN = 4
POWER_LED_PIN = 19
NETWORK_LED_PIN = 20
COUNTS_LED_PIN = 21

# Note: GPIO.LOW  - 0V
#       GPIO.HIGH - 3.3V or 5V ???? (RPi rail voltage)

DEFAULT_CONFIG = '/home/pi/config/config.csv'
DEFAULT_PUBLICKEY = '/home/pi/config/id_rsa_lbl.pub'
DEFAULT_HOSTNAME = 'dosenet.dhcp.lbl.gov'
DEFAULT_PORT = 5005

DEFAULT_INTERVAL_NORMAL = 300
DEFAULT_INTERVAL_TEST = 30

# ANSI color codes
ANSI_RESET = '\033[0m'
ANSI_BOLD = '\033[1m'
ANSI_YEL = '\033[33m' + ANSI_BOLD
ANSI_GR = '\033[32m' + ANSI_BOLD

# this is hacky, but, the {{}} get converted to {} in the first .format() call
#   and then get filled in later
CPM_DISPLAY_TEXT = (
    '{{time}}: {yellow} {{counts}} cts{reset}' +
    ' --- {green}{{cpm:.2f}} +/- {{cpm_err:.2f}} cpm{reset}' +
    ' ({{start_time}} to {{end_time}})').format(
    yellow=ANSI_YEL, reset=ANSI_RESET, green=ANSI_GR)


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
                 verbosity=1,
                 ):

        self.v = verbosity

        # resolve defaults that depend on test mode
        if test:
            if interval is None:
                interval = DEFAULT_INTERVAL_TEST
        else:
            if interval is None:
                interval = DEFAULT_INTERVAL_NORMAL
            if config is None:
                config = DEFAULT_CONFIG
            if publickey is None:
                publickey = DEFAULT_PUBLICKEY

        if RPI:
            self.power_LED = LED(power_LED_pin)
            self.network_LED = LED(network_LED_pin)
            self.counts_LED = LED(counts_LED_pin)

            self.power_LED.on()
        else:
            self.power_LED = None
            self.network_LED = None
            self.counts_LED = None

        if config:
            self.config = Config(config)
        else:
            print('WARNING: no config file given. Not posting to server')
            self.config = None

        if publickey:
            self.publickey = PublicKey(publickey)
        else:
            print('WARNING: no public key given. Not posting to server')
            self.publickey = None

        self.sensor = Sensor(
            counts_LED=self.counts_LED,
            verbosity=self.v)
        self.network_up = NetworkStatus(
            network_led=self.network_LED,
            verbosity=self.v)
        self.sender = ServerSender(
            manager=self,
            verbosity=self.v)

        self.interval = interval
        self.running = False

    def run(self):
        """
        Start counting time.

        This method does NOT return, so run in a subprocess if you
        want to keep control.

        However, setting self.running = False will stop, as will a
          KeyboardInterrupt.
        """

        this_start = time.time()
        if self.v > 0:
            print(('Manager is starting to run at {}' +
                   ' with intervals of {}s').format(
                       datetime_from_epoch(this_start), self.interval))
        this_end = this_start + self.interval
        self.running = True
        strf = '%H:%M:%S'

        try:
            while self.running:
                sleeptime = this_end - time.time()
                time.sleep(sleeptime)
                assert time.time() > this_end
                cpm, cpm_err = self.sensor.get_cpm(this_start, this_end)
                counts = int(round(cpm * self.interval / 60))

                start_text = datetime_from_epoch(this_start).strftime(strf)
                end_text = datetime_from_epoch(this_end).strftime(strf)

                print(CPM_DISPLAY_TEXT.format(
                    time=datetime_from_epoch(time.time()),
                    counts=counts,
                    cpm=cpm,
                    cpm_err=cpm_err,
                    start_time=start_text,
                    end_time=end_text,
                ))
                self.sender.send_cpm(cpm, cpm_err)

                this_start = this_end
                this_end = this_end + self.interval
        except KeyboardInterrupt:
            print('KeyboardInterrupt: stopping Manager run')
            self.stop()

    def stop(self):
        """Stop counting time."""
        self.running = False

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
            '--verbosity', '-v', type=int, default=1,
            help='Verbosity level (0 to 3) (default 1)')
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


if __name__ == '__main__':
    mgr = Manager.from_argparse()
    mgr.run()
