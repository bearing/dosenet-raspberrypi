#!/home/pi/miniconda/bin/python
# -*- coding: utf-8 -*-
#
# Ryan Pavlovsky (until Mon Jun 15 2015)
# Navrit Bal (Jun 15 2015 to Aug 2015)
# Brian Plimley, Joseph Curtis, Ali Hanks (after Aug 2015)
# DoseNet
# Applied Nuclear Physics Division
# Lawrence Berkeley National Laboratory, Berkeley, U.S.A.
# Originally adapted from dosimeter.py (Ryan Pavlovsky)
#################################
# Indirectly run on Raspberry Pis
#################################

from __future__ import print_function

import RPi.GPIO as GPIO
import numpy as np
import datetime
import multiprocessing
from time import sleep
import os
import csv
import cust_crypt
import socket
import collections
# collections.deque object allows fast popping from left side

# Count seconds from the year 1970
# This is like Unix time, but without handling time zones.
# *** If times from a different clock or time zone are passed into Dosimeter,
#   there would be problems....
# So even if the RPi is in some weird state where it thinks its the 1990s...
#   it will still work because everything is a relative measure of seconds.
EPOCH_START_TIME = datetime.datetime(year=1970, month=1, day=1)

# SIG >> float (~3.3V) --> 0.69V --> EXP charge back to float (~3.3V)
# NS  >> ~0V (GPIO.LOW) --> 3.3V (GPIO.HIGH) RPi rail

# Standard pin numbers (Broadcom):
SIGNAL_PIN = 17
NOISE_PIN = 4
NETWORK_LED_PIN = 20
POWER_LED_PIN = 26
COUNTS_LED_PIN = 21

# Note: GPIO.LOW  - 0V
#       GPIO.HIGH - 3.3V or 5V ???? (RPi rail voltage)


class Manager(object):
    """
    Master object for dosimeter operation.

    Initializes Dosimeter, LEDs and DosimeterCommunicator,
    tracks time intervals, and converts the counts from Dosimeter into
    a CPM for ___ to give to the buffers and the server.

    time_interval_s is the interval (in seconds) over for which CPM is
    calculated.
    """

    def __init__(self,
                 network_LED_pin=NETWORK_LED_PIN,
                 power_LED_pin=POWER_LED_PIN,
                 counts_LED_pin=COUNTS_LED_PIN,
                 signal_pin=SIGNAL_PIN,
                 noise_pin=NOISE_PIN,
                 time_interval_s=300,
                 config_csv_path=None,
                 public_key_path=None,
                 ):

        self.network_LED = LED(network_LED_pin)
        self.power_LED = LED(power_LED_pin)
        self.counts_LED = LED(counts_LED_pin)

        if config_csv_path:
            # TODO: handle config_csv_path=None as well as IOError here
            self.config = Config(config_csv_path)
        else:
            print('WARNING: no config file given. Not posting to server')

        if public_key_path:
            # TODO
            pass
            self.public_key = False
        else:
            pass

        self.power_LED.on()
        self.dosimeter = Dosimeter(counts_LED=self.counts_LED)
        self.network_up = NetworkStatus(network_led=self.network_LED)

        self.DT = time_interval_s
        # TODO: standardize all these timedeltas and floats in a nice way
        self.running = False

    def start(self):
        """
        Start counting time.

        This method does NOT return, so run in a subprocess if you
        want to keep control.
        """

        this_start = datetime.datetime.now()
        self.running = True

        while self.running:
            pass
            sleep(10)

    def stop(self):
        """Stop counting time."""
        self.running = False


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
      verbosity=1
        verbosity 0: nothing printed
        verbosity 1: only network down printed
        verbosity 2: always printed

    Output:
      use the __bool__() function
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
                 verbosity=1):
        self.hostname = hostname
        self.up_interval_s = up_interval_s
        self.down_interval_s = down_interval_s
        self.led = network_led
        self.blink_period_s = 1.5
        self.v = verbosity

        self.is_up = False

        self._p = multiprocessing.Process(target=self._do_pings)
        self._p.start()

    def update(self):
        """Update network status"""

        response = self._ping()
        if response == 0:
            self.is_up = True
            if self.led:
                if self.led.blinker:
                    self.led.stop_blink()
                self.led.on()
            if self.v > 1:
                print('  {} is UP'.format(self.hostname))
        else:
            self.is_up = False
            if self.led:
                self.led.start_blink(interval=self.blink_period_s)
            if self.v > 0:
                print('  {} is DOWN!'.format(self.hostname))

    def _do_pings(self):
        """Runs forever - only call as a subprocess"""
        while True:
            self.update()
            if self:
                sleep(self.up_interval_s)
            else:
                sleep(self.down_interval_s)

    def _ping(self):
        """one ping"""
        return os.system('ping -c 1 {} > /dev/null'.format(self.hostname))

    def __bool__(self):
        return self.is_up


class Config(object):
    """
    Represents the CSV configuration file.
    """

    def __init__(self, filename):
        try:
            with open(filename, 'rb') as config_file:
                config_reader = csv.DictReader(config_file)
                content = config_reader.next()
        except IOError:
            print('IOError loading config file.',
                  'Check filename, path, permissions?')
            return None

        self.ID = content['stationID']
        self.hash = content['message_hash']
        self.lat = content['lat']
        self.long = content['long']


class Dosimeter(object):
    """
    Dosimeter takes counts from the sensor, flashing the LED and adding to a
    queue of counts. CPM should be calculated by something external.

    counts_LED: an LED object
    max_accumulation_time_s: events are forgotten after this length of time
    """

    def __init__(self, counts_LED=None, max_accumulation_time_s=3600):

        if counts_LED is None:
            print('No LED given for counts; will not flash LED!')
        self.LED = counts_LED
        # initialize queue of datetime's
        self.counts = collections.deque([])
        self.accum_time = datetime.timedelta(seconds=max_accumulation_time_s)

        # use Broadcom GPIO numbering
        GPIO.setmode(GPIO.BCM)
        # set up signal pin
        GPIO.setup(SIGNAL_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        self.add_interrupt()

    def add_interrupt(self):
        """
        Setup GPIO for signal. (for initialization and GPIO reset)
        """
        GPIO.add_event_detect(
            SIGNAL_PIN, GPIO.FALLING,
            callback=self.count,
            bouncetime=1)

    def count(self, pin=SIGNAL_PIN):
        """
        Add one count to queue. (Callback for GPIO pin)

        pin argument is automatically supplied by GPIO.add_event_detect
        """

        # add to queue
        now = datetime.datetime.now()
        self.counts.append(now_float())

        # display(s)
        print('\tCount at {}'.format(now))
        if self.LED:
            self.LED.flash()

    def get_all_counts(self):
        """Return the list of all counts"""

        self.check_accumulation()

        # should this be a copy or something? need to be careful
        return self.counts

    def check_accumulation(self):
        """Remove counts that are older than accum_time"""

        while self.counts:      # gotta make sure it's not an empty queue
            if self.counts[0] > time_float(
                    datetime.datetime.now() - self.accum_time):
                # done
                break
            self.counts.popleft()

    def reset_GPIO(self):
        """
        Older code does this every loop. I don't know whether it's needed.
        """
        GPIO.remove_event_detect(SIGNAL_PIN)
        self.add_interrupt()

    def cleanup(self):
        print('Cleaning up GPIO pins')
        GPIO.cleanup()

    def __del__(self):
        print('Deleting Dosimeter instance {}'.format(self))
        self.cleanup()

    def __enter__(self):
        # required for using in 'with'
        return self

    def __exit__(self, *args):
        print('Exiting Dosimeter instance {}'.format(self))
        self.cleanup()


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

        GPIO.setmode(GPIO.BCM)
        GPIO.setup(pin, GPIO.OUT)
        self.pin = pin
        self.blinker = None

    def on(self):
        """Turn on the LED"""
        GPIO.output(self.pin, True)

    def off(self):
        """Turn off the LED"""
        GPIO.output(self.pin, False)

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


class DataManager(object):
    """
    Handles the passing of the CPM between DosimeterTimer, memory buffer,
    local storage, and ServerSender.
    """

    pass


class ServerSender(object):
    """
    Sends UDP packets to the DoseNet server.
    """

    # TODO: include verbosity for test mode

    def __init__(self, manager):
        self.manager = manager
        # check that config and publickey exist and are valid
        self.encrypter = cust_crypt.PublicDEncrypt(
            key_file_lst=[self.manager.public_key])
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        # TODO: load these from somewhere
        self.address = 'dosenet.dhcp.lbl.gov'
        self.port = 5005

    def construct_packet(self, cpm, cpm_error, error_code=0):
        """basically copied from old code"""

        c = ','
        config = self.manager.config
        raw_packet = (
            str(config.hash) + c +
            str(config.ID) + c +
            str(cpm) + c +
            str(cpm_error) + c +
            str(error_code))
        encrypted_packet = self.encrypter.encrypt_message(raw_packet)[0]

        return encrypted_packet

    def send_packet(self, encrypted_packet):
        """basically copied from old code"""

        self.socket.sendto(encrypted_packet, (self.address, self.port))
        # TODO: try/except


def time_float(a_datetime):
    """
    Return a float indicating number of seconds from EPOCH_START_TIME
    to the input
    """
    return (a_datetime - EPOCH_START_TIME).total_seconds()


def now_float():
    """
    Return a float indicating number of seconds since EPOCH_START_TIME
    """
    return time_float(datetime.datetime.now())


def test():
    """
    Test suite
    """

    # Clean up everything in case of bad previous session
    for pin in (
            SIGNAL_PIN,
            NOISE_PIN,
            NETWORK_LED_PIN,
            COUNTS_LED_PIN,
            POWER_LED_PIN):
        try:
            GPIO.cleanup(pin)
        except RuntimeWarning:
            # 'No channels have been set up yet - nothing to clean up!'
            pass

    print('Testing LED class...')
    test_LED()

    print('Testing Dosimeter class. KeyboardInterrupt to skip..')
    try:
        test_Dosimeter()
    except KeyboardInterrupt:
        print('  Okay, skipping remaining Dosimeter tests!')


def test_LED():
    led = LED(pin=NETWORK_LED_PIN)
    print('  LED on')
    led.on()
    sleep(1)
    print('  LED off')
    led.off()
    sleep(1)
    print('  LED flash')
    led.flash()
    sleep(1)
    print('  LED start blink')
    led.start_blink()
    sleep(3.2)
    # stop mid-blink. the LED should turn off.
    print('  LED stop blink')
    led.stop_blink()
    sleep(0.5)


def test_Dosimeter():
    test_accum_time = 30
    print('  Creating Dosimeter with max_accumulation_time_s={}'.format(
        test_accum_time))
    with Dosimeter(max_accumulation_time_s=test_accum_time) as d:
        print('  Testing check_accumulation() on empty queue')
        d.check_accumulation()
        print('  Waiting for counts')
        max_test_time_s = datetime.timedelta(seconds=300)
        start_time = datetime.datetime.now()

        first_count_time_float = None
        while datetime.datetime.now() - start_time < max_test_time_s:
            sleep(10)
            if d.get_all_counts():
                first_count_time_float = d.get_all_counts()[0]
                break
        else:
            # "break" skips over this
            print('    Got no counts in {} seconds! May be a problem.'.format(
                max_test_time_s.total_seconds()),
                'Skipping accumulation test')
        if first_count_time_float:
            # accumulation test
            test_Dosimeter_accum(d, first_count_time_float, test_accum_time)


def test_Dosimeter_accum(d, first_count_time_float, test_accum_time):
    """ accumulation test """
    end_time_s = first_count_time_float + test_accum_time + 5
    wait_time_s = (end_time_s - now_float())
    print('  Accumulation test; waiting another {} s'.format(wait_time_s))
    sleep(wait_time_s)
    # get_all_counts() calls check_accumulation(), so don't use it here
    n = len(d.counts)

    d.check_accumulation()
    # the first count ought to be removed now
    assert len(d.get_all_counts()) < n
    # also make sure there are no counts within accum time
    if d.get_all_counts():
        assert now_float() - d.get_all_counts()[0] < test_accum_time


if __name__ == '__main__':
    pass
