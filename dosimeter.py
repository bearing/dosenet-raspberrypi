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


class DosimeterTimer(object):
    """
    Master object for dosimeter operation.

    Initializes Dosimeter, LEDs and DosimeterCommunicator,
    tracks time intervals, and converts the counts from Dosimeter into
    a CPM for DosimeterCommunicator to give to the buffers and the server.

    time_interval_s is the interval (in seconds) over for which CPM is
    calculated.
    """

    def __init__(self,
                 network_LED_pin=NETWORK_LED_PIN,
                 power_LED_pin=POWER_LED_PIN,
                 counts_LED_pin=COUNTS_LED_PIN,
                 signal_pin=SIGNAL_PIN,
                 noise_pin=NOISE_PIN,
                 time_interval_s=300):

        self.network_LED = LED(network_LED_pin)
        self.power_LED = LED(power_LED_pin)
        self.counts_LED = LED(counts_LED_pin)

        self.power_LED.on()
        self.dosimeter = Dosimeter(counts_LED=self.counts_LED)

        self.DT = time_interval_s
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
        time_float = (now - EPOCH_START_TIME).total_seconds()
        self.counts.append(time_float)

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

        now = datetime.datetime.now()
        if self.counts:
            while self.counts[0] < (now - self.accum_time):
                self.counts.popleft()

    def reset_GPIO(self):
        pass

    def cleanup(self):
        GPIO.cleanup()

    def __del__(self):
        print('Deleting Dosimeter instance {}'.format(self))
        self.cleanup()

    def __exit__(self):
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
        self.blinking = False
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
        self.blinking = True
        self.blinker = multiprocessing.Process(
            target=self.do_blink, kwargs={'interval': interval})
        self.blinker.start()

    def stop_blink(self):
        """Switch off the blinking state of the LED"""
        self.blinking = False
        if self.blinker:
            self.blinker.terminate()

    def do_blink(self, interval=1):
        """
        Run this method as a subprocess only!

        It blinks until self.blinking = False.
        """

        while self.blinking:
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

    pass


if __name__ == '__main__':
    pass
