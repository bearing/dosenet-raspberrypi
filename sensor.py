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
from time import sleep
import collections

from auxiliaries import LED

EPOCH_START_TIME = datetime.datetime(year=1970, month=1, day=1)
# Standard pin numbers (Broadcom):
SIGNAL_PIN = 17
NOISE_PIN = 4
NETWORK_LED_PIN = 20
POWER_LED_PIN = 26
COUNTS_LED_PIN = 21


class Sensor(object):
    """
    Sensor takes counts from the sensor, flashing the LED and adding to a
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

        # TODO: check_accumulation every 5 minutes or so?
        #       to prevent memory leak if it gets abandoned?

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
        now2 = datetime.datetime.now()

        # display(s)
        print('\tCount at {}'.format(now))
        if self.LED:
            self.LED.flash()
        print('    Adding count to queue took no more than {} s'.format(
            (now2 - now).total_seconds()))

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
        n_counts = np.sum(counts > start_time & counts < end_time)
        err_counts = np.sqrt(n_counts)
        dt = end_time - start_time
        cps = n_counts / dt
        cps_err = err_counts / dt
        cpm = cps / 60
        cpm_err = cps_err / 60

        return cpm, cpm_err

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
        print('Deleting Sensor instance {}'.format(self))
        self.cleanup()

    def __enter__(self):
        # required for using in 'with'
        return self

    def __exit__(self, *args):
        print('Exiting Sensor instance {}'.format(self))
        self.cleanup()


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

    print('Testing Sensor class. KeyboardInterrupt to skip..')
    try:
        test_Sensor()
    except KeyboardInterrupt:
        print('  Okay, skipping remaining Sensor tests!')


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


def test_Sensor():
    test_accum_time = 30
    print('  Creating Sensor with max_accumulation_time_s={}'.format(
        test_accum_time))
    with Sensor(max_accumulation_time_s=test_accum_time) as d:
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
            test_Sensor_accum(d, first_count_time_float, test_accum_time)


def test_Sensor_accum(d, first_count_time_float, test_accum_time):
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
