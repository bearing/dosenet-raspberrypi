# -*- coding: utf-8 -*-
from __future__ import print_function

import datetime
from time import sleep

from auxiliaries import LED, Config, NetworkStatus
from sensor import Sensor
from sender import ServerSender
import argparse

# Count seconds from the year 1970
# This is like Unix time, but without handling time zones.
# *** If times from a different clock or time zone are passed into Sensor,
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

    Initializes other classes, tracks time intervals, and converts the counts
    from Sensor into a CPM to give to the server.

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
        self.sensor = Sensor(counts_LED=self.counts_LED)
        self.network_up = NetworkStatus(network_led=self.network_LED)
        self.sender = ServerSender(self)

        self.DT = time_interval_s
        # TODO: standardize all these timedeltas and floats in a nice way
        self.running = False

    def run(self):
        """
        Start counting time.

        This method does NOT return, so run in a subprocess if you
        want to keep control. However, setting self.running = False will stop.
        """

        this_start = datetime.datetime.now()
        this_end = this_start + self.DT
        self.running = True

        while self.running:
            sleeptime = this_end - datetime.datetime.now()
            sleep(sleeptime)
            assert datetime.datetime.now() > this_end
            cpm, cpm_err = self.sensor.get_cpm(this_start, this_end)
            self.sender.send_cpm(cpm, cpm_err)

            this_start = this_end
            this_end = this_end + self.DT

    def stop(self):
        """Stop counting time."""
        self.running = False

    @classmethod
    def from_args(cls):
        parser = argparse.ArgumentParser()
