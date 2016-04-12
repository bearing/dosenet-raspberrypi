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
import time
import collections

from auxiliaries import LED, datetime_from_epoch

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

    def __init__(self,
                 counts_LED=None,
                 max_accumulation_time_s=3600,
                 verbosity=1,
                 ):

        self.v = verbosity

        if counts_LED is None:
            print('No LED given for counts; will not flash LED!')
        self.LED = counts_LED
        # initialize queue of datetime's
        self.counts = collections.deque([])
        self.accum_time = max_accumulation_time_s

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
        except RuntimeError as e:
            if self.v > 1:
                print('GPIO interrupt setup failed',
                      '({} tries remaining)'.format(n_tries))
            # Happened once in testing. It worked on second try.

            if n_tries < 1:
                raise e
            else:
                time.sleep(1)
                self.add_interrupt(n_tries=(n_tries - 1))

    def count(self, pin=SIGNAL_PIN):
        """
        Add one count to queue. (Callback for GPIO pin)

        pin argument is automatically supplied by GPIO.add_event_detect
        """

        # add to queue
        now = time.time()
        self.counts.append(now)
        now2 = time.time()

        # display(s)
        print('\tCount at {}'.format(datetime_from_epoch(now)))
        if self.LED:
            self.LED.flash()
        if self.v > 1:
            print('    Adding count to queue took no more than {} s'.format(
                (now2 - now)))

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

        # debug
        lg1 = counts > start_time
        lg2 = counts < end_time
        lg3 = lg1 & lg2
        n_counts = np.sum(lg3)
        # n_counts = np.sum(counts > start_time & counts < end_time)

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
            if self.counts[0] > time.time() - self.accum_time:
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
    time.sleep(1)
    print('  LED off')
    led.off()
    time.sleep(1)
    print('  LED flash')
    led.flash()
    time.sleep(1)
    print('  LED start blink')
    led.start_blink()
    time.sleep(3.2)
    # stop mid-blink. the LED should turn off.
    print('  LED stop blink')
    led.stop_blink()
    time.sleep(0.5)


def test_Sensor():
    test_accum_time = 30
    print('  Creating Sensor with max_accumulation_time_s={}'.format(
        test_accum_time))
    with Sensor(max_accumulation_time_s=test_accum_time) as d:
        print('  Testing check_accumulation() on empty queue')
        d.check_accumulation()
        print('  Waiting for counts')
        max_test_time_s = 300
        start_time = time.time()

        first_count_time_float = None
        while time.time() - start_time < max_test_time_s:
            time.sleep(10)
            if d.get_all_counts():
                first_count_time_float = d.get_all_counts()[0]
                break
        else:
            # "break" skips over this
            print('    Got no counts in {} seconds! May be a problem.'.format(
                max_test_time_s),
                'Skipping accumulation test')
        if first_count_time_float:
            # accumulation test
            test_Sensor_accum(d, first_count_time_float, test_accum_time)


def test_Sensor_accum(d, first_count_time_float, test_accum_time):
    """ accumulation test """
    end_time_s = first_count_time_float + test_accum_time + 5
    wait_time_s = (end_time_s - time.time())
    print('  Accumulation test; waiting another {} s'.format(wait_time_s))
    time.sleep(wait_time_s)
    # get_all_counts() calls check_accumulation(), so don't use it here
    n = len(d.counts)

    d.check_accumulation()
    # the first count ought to be removed now
    assert len(d.get_all_counts()) < n
    # also make sure there are no counts within accum time
    if d.get_all_counts():
        assert time.time() - d.get_all_counts()[0] < test_accum_time


if __name__ == '__main__':
    pass
