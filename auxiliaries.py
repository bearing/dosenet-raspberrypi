# -*- coding: utf-8 -*-
from __future__ import print_function

import datetime
import multiprocessing
import csv
from time import sleep
import os
import traceback
import time
import sys

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
            else:
                print(*args, **kwargs)
                sys.stdout.flush()

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
            self.is_on = False
        else:
            raise EnvironmentError('Must be a Raspberry Pi to have an LED')

    def on(self):
        """Turn on the LED"""
        GPIO.output(self.pin, True)
        self.is_on = True

    def off(self):
        """Turn off the LED"""
        try:
            GPIO.output(self.pin, False)
            self.is_on = False
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
