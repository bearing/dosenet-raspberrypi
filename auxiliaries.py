# -*- coding: utf-8 -*-
from __future__ import print_function

import datetime
import multiprocessing
import csv
from time import sleep
import os
import traceback
import time

from globalvalues import RPI
if RPI:
    import RPi.GPIO as GPIO

from globalvalues import DEFAULT_DATALOG

import cust_crypt


def datetime_from_epoch(timestamp):
    """
    Return a datetime object equivalent to the number of seconds since
    Unix epoch (Jan 1, 1970).

    The datetime object is in UTC.
    """

    datetime_value = (datetime.datetime(year=1970, month=1, day=1) +
                      datetime.timedelta(seconds=timestamp))
    return datetime_value


def set_verbosity(class_instance, verbosity=None, logfile=None):
    """
    Define the verbosity level for any class instance,
    by generating a custom print method, 'vprint', for the instance.

    The vprint method can take arguments exactly like the print function,
    except that first there is a required argument, v, which is the minimum
    verbosity for the printing to happen.

    If verbosity is not given, get it from class_instance.v.

    Additionally, logging is supported. If a logfile argument is passed,
    it should be a string indicating a file to write into.
    The log contains the same text that gets printed.

    Usage example:
      def __init__(self, verbosity=1):
          set_verbosity(self, verbosity=verbosity)
      ...
      self.vprint(2, 'This only prints if verbosity >= 2')
    """

    if verbosity is None:
        verbosity = class_instance.v

    if logfile is None:
        logging = False
    else:
        logging = True

    def vprint(level, *args, **kwargs):
        """
        The conditional print function, to be returned.
        """

        if verbosity >= level:
            print(*args, **kwargs)
            if logging:
                # first, have to handle the print function
                # there could be multiple string arguments which need
                #   concatenating
                s = ''
                for a in args:
                    s += a
                full_string = str(datetime.datetime.now()) + ': ' + s + '\n'
                try:
                    with open(logfile, 'a') as lf:
                        lf.write(full_string)
                except IOError:
                    print(' * Logging failed - IOError')

    class_instance.vprint = vprint


def get_data(base_path=DEFAULT_DATALOG):
    """
    Argument is the path where the data-log is. Default is DEFAULT_DATALOG
    """

    with open(base_path) as inputfile:
        results = list(csv.reader(inputfile))
    return results


class LED(object):
    """
    Represents one LED, available for blinking or steady operation.

    Methods/usage:

    myLED = LED(broadcom_pin_number)
    myLED.on()
    myLED.off()
    myLED.flash()   # single flash, like for a count
    myLED.start_blink(interval=1)   # set the LED blinking in a subprocess
                                    # interval is the period of blink
    myLED.stop_blink()
    """

    def __init__(self, pin):
        """
        Initialize a pin for operating an LED. pin is the Broadcom GPIO #
        """

        if RPI:
            GPIO.setmode(GPIO.BCM)
            GPIO.setup(pin, GPIO.OUT)
            self.pin = pin
            self.blinker = None
        else:
            raise EnvironmentError('Must be a Raspberry Pi to have an LED')

    def on(self):
        """Turn on the LED"""
        GPIO.output(self.pin, True)

    def off(self):
        """Turn off the LED"""
        try:
            GPIO.output(self.pin, False)
        except RuntimeError:
            # if GPIO is cleaned up too early
            pass

    def flash(self):
        """Flash the LED once"""
        self.on()
        sleep(0.005)
        self.off()

    def start_blink(self, interval=1):
        """
        Set the LED in a blinking state using a subprocess.

        interval is the period of the blink, in seconds.
        """

        if self.blinker:
            self.blinker.terminate()
            # this is maybe not necessary, but seems safer
        self.blinker = multiprocessing.Process(
            target=self._do_blink, kwargs={'interval': interval})
        self.blinker.start()

    def stop_blink(self):
        """Switch off the blinking state of the LED"""
        if self.blinker:
            self.blinker.terminate()
        self.off()

    def _do_blink(self, interval=1):
        """
        Run this method as a subprocess only!

        It blinks forever (until terminated).
        """

        while True:
            self.on()
            sleep(interval / 2.0)
            self.off()
            sleep(interval / 2.0)


class NetworkStatus(object):
    """
    Keep track of network status.

    Inputs:
      hostname='dosenet.dhcp.lbl.gov'
        hostname to ping
      up_interval_s=300
        this is the interval between pings, if the network was up
      down_interval_s=5
        this is the interval between pings, if the network was down
      network_led=None
        an instance of LED class
      pinging=True
        instantiate the object with live pinging
      verbosity=1
        verbosity 0: nothing printed
        verbosity 1: only network down printed
        verbosity 2: always printed

    Output:
      use the __nonzero__() function
      e.g.:
      ns = NetworkStatus()
      if ns:
          # network is up
    """

    def __init__(self,
                 hostname='dosenet.dhcp.lbl.gov',
                 up_interval_s=300,
                 down_interval_s=5,
                 network_led=None,
                 pinging=True,
                 verbosity=1,
                 logfile=None,
                 ):
        self.hostname = hostname
        self.up_interval_s = up_interval_s
        self.down_interval_s = down_interval_s
        self.led = network_led
        self.blink_period_s = 1.5
        self.last_try_time = None

        self.logfile = logfile
        self.v = verbosity
        set_verbosity(self, logfile=logfile)

        init_state = 'N'    # for None
        self.up_state = multiprocessing.Value('c', init_state)

        self._p = None
        if pinging:
            self.start_pinging()
        else:
            self.pinging = False

    def start_pinging(self):
        """Start the subprocess that pings at intervals"""
        if self._p:
            self._p.terminate()
        self._p = multiprocessing.Process(
            target=self._do_pings,
            args=(self.up_state,))
        self._p.start()
        self.pinging = True

    def stop_pinging(self):
        """Stop the subprocess that pings at intervals"""
        if self._p:
            self._p.terminate()
        self.pinging = False

    def update(self, up_state=None):
        """
        Update network status.

        up_state is the shared memory object for the pinging process.
        If calling update() manually, leave it as None (default).
        """
        if not self.last_try_time:
            self.last_try_time = time.time()

        if up_state is None:
            up_state = self.up_state

        response = self._ping()
        if response == 0:
            self.last_try_time = time.time()
            up_state.value = 'U'
            if self.led:
                if self.led.blinker:
                    self.led.stop_blink()
                self.led.on()
            self.vprint(2, '  {} is UP'.format(self.hostname))
        else:
            up_state.value = 'D'
            self.vprint(1, '  {} is DOWN!'.format(self.hostname))
            self.vprint(3, 'Network down for {} seconds'.format(
                time.time() - self.last_try_time))
            if self.led:
                self.led.start_blink(interval=self.blink_period_s)
            if time.time() - self.last_try_time >= 1800:
                self.vprint(1, 'Making network go back up')
                os.system("sudo ifdown wlan1")
                os.system("sudo ifup wlan1")
                self.last_try_time = time.time()

    def _do_pings(self, up_state):
        """Runs forever - only call as a subprocess"""
        try:
            while True:
                self.update(up_state=up_state)
                if self:
                    sleep(self.up_interval_s)
                else:
                    sleep(self.down_interval_s)
        except:
            if self.logfile:
                with open(self.logfile, 'a') as f:
                    traceback.print_exc(15, f)

    def _ping(self):
        """one ping"""
        return os.system('ping -c 1 {} > /dev/null'.format(self.hostname))

    def _get_state(self):
        if self.up_state.value == 'U':
            return True
        if self.up_state.value == 'D':
            return False
        else:
            self.update()
            return self._get_state()

    def __bool__(self):
        return self._get_state()

    # python2 uses __nonzero__ for __bool__
    def __nonzero__(self):
        return self._get_state()

    def cleanup(self):
        GPIO.cleanup()
        if self._p:
            self._p.terminate()
        self.pinging = False


class Config(object):
    """
    Represents the CSV configuration file.
    """

    def __init__(self, filename, verbosity=1, logfile=None):
        set_verbosity(self, verbosity=verbosity, logfile=logfile)
        with open(filename, 'rb') as config_file:
            config_reader = csv.DictReader(config_file)
            content = config_reader.next()

        self.ID = content['stationID']
        self.hash = content['message_hash']
        try:
            self.lat = content['lat']
        except KeyError:
            self.vprint(1, "WARNING: config file key error.",
                        "Check for 'lag' instead of 'lat'")
            self.lat = content['lag']
        self.long = content['long']


class PublicKey(object):
    """
    Represents the public key file.
    """

    def __init__(self, filename, verbosity=1, logfile=None):
        set_verbosity(self, verbosity=verbosity, logfile=logfile)

        self.encrypter = cust_crypt.PublicDEncrypt(
            key_file_lst=[filename])
        if not self.encrypter.public_key:
            self.encrypter = None
            self.vprint(
                1, 'Failed to load public key file, {}!'.format(filename))
