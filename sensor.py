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

import numpy as np
import time
import collections
import traceback

from globalvalues import RPI
if RPI:
    import RPi.GPIO as GPIO

from auxiliaries import datetime_from_epoch, set_verbosity
from globalvalues import SIGNAL_PIN
from globalvalues import DEFAULT_MAX_ACCUM_TIME


class Sensor(object):
    """
    Sensor takes counts from the sensor, flashing the LED and adding to a
    queue of counts. CPM should be calculated by something external.

    counts_LED: an LED object
    max_accumulation_time_s: events are forgotten after this length of time
    use_gpio: flag for actually using the GPIO pins. Set to False for testing
    verbosity: 0-3
    """

    def __init__(self,
                 counts_LED=None,
                 max_accumulation_time_s=DEFAULT_MAX_ACCUM_TIME,
                 use_gpio=None,
                 verbosity=1,
                 logfile=None,
                 ):

        self.v = verbosity
        self.logfile = logfile
        set_verbosity(self, logfile=logfile)

        if use_gpio is None:
            self.use_gpio = RPI
        else:
            self.use_gpio = use_gpio
        if not self.use_gpio:
            self.vprint(1, 'Running Sensor in test mode - no GPIO interrupt')
            # this "test mode" is not the same as manager.py test mode!
            # manager test mode runs the sensor normally.
            # sensor test mode is a software-only construct - no sensor
            #   hardware involved

        if counts_LED is None:
            self.vprint(1, 'No LED given for counts; will not flash LED!')
        self.LED = counts_LED
        # initialize queue of datetime's
        self.counts = collections.deque([])
        self.accum_time = max_accumulation_time_s

        if RPI:
            # use Broadcom GPIO numbering
            GPIO.setmode(GPIO.BCM)
            # set up signal pin
            GPIO.setup(SIGNAL_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
            self.add_interrupt()

        # TODO: check_accumulation every 5 minutes or so?
        #       to prevent memory leak if it gets abandoned?

    def add_interrupt(self, n_tries=3):
        """
        Setup GPIO for signal. (for initialization and GPIO reset)
        """

        try:
            GPIO.add_event_detect(
                SIGNAL_PIN, GPIO.FALLING,
                callback=self.count,
                bouncetime=1)
        except RuntimeError:
            if self.v > 1:
                self.vprint(1, 'GPIO interrupt setup failed',
                            '({} tries remaining)'.format(n_tries))
            # Happened once in testing. It worked on second try.

            if n_tries < 1:
                raise
            else:
                time.sleep(1)
                self.add_interrupt(n_tries=(n_tries - 1))

    def count(self, pin=SIGNAL_PIN):
        """
        Add one count to queue. (Callback for GPIO pin)

        pin argument is supplied by GPIO.add_event_detect, do not remove
        """

        # watching for stray errors... (temp?)
        try:
            # add to queue. (usually takes ~10 us)
            now = time.time()
            self.counts.append(now)

            # display(s)
            self.vprint(1, '\tCount at {}'.format(datetime_from_epoch(now)))
            if self.LED:
                self.LED.flash()
        except:
            if self.logfile:
                with open(self.logfile, 'a') as f:
                    traceback.print_exc(15, f)
            raise

    def get_all_counts(self):
        """Return the list of all counts"""

        self.check_accumulation()

        # should this be a copy or something? need to be careful
        return self.counts

    def get_cpm(self, start_time, end_time):
        """Measure the CPM between start_time and end_time."""

        counts = np.array(self.get_all_counts())
        # np.array(deque) makes a copy of the data.
        # there could be more optimal ways to pass around the data,
        #   but it only happens every ~5 minutes anyway.
        #   just as long as there's no memory issue.

        n_counts = np.sum((counts > start_time) & (counts < end_time))

        err_counts = np.sqrt(n_counts)
        dt = end_time - start_time
        cps = float(n_counts) / dt
        cps_err = float(err_counts) / dt
        cpm = cps * 60
        cpm_err = cps_err * 60

        return cpm, cpm_err

    def check_accumulation(self):
        """Remove counts that are older than accum_time"""

        try:
            while self.counts[0] < time.time() - self.accum_time:
                self.counts.popleft()
        except IndexError:      # empty queue
            pass

    def reset_GPIO(self):
        """
        Older code does this every loop. I don't know whether it's needed.
        As of this refactoring, the device runs fine (for 24 hrs) without.
        """
        GPIO.remove_event_detect(SIGNAL_PIN)
        self.add_interrupt()

    def cleanup(self):
        if RPI:
            self.vprint(1, 'Cleaning up GPIO pins')
            GPIO.cleanup()

    def __del__(self):
        print('Deleting Sensor instance {}'.format(self))
        self.cleanup()

    def __enter__(self):
        # required for using in 'with'
        return self

    def __exit__(self, *args):
        print('Exiting Sensor instance {}'.format(self))
        self.cleanup()


if __name__ == '__main__':
    pass
