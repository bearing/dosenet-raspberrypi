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

import RPi.GPIO as GPIO
import numpy as np
import datetime
from time import sleep
import os
import collections
# collections.deque object allows fast popping from left side

SIG_PIN = 17
NS_PIN = 4

# Count seconds from the year 1970
# This is like Unix time, but without handling time zones.
# *** If times from a different clock or time zone are passed into Dosimeter,
#   there would be problems....
# So even if the RPi is in some weird state where it thinks its the 1990s...
#   it will still work because everything is a relative measure of seconds.
EPOCH_START_TIME = datetime.datetime(year=1970, month=1, day=1)

# SIG >> float (~3.3V) --> 0.69V --> EXP charge back to float (~3.3V)
# NS  >> ~0V (GPIO.LOW) --> 3.3V (GPIO.HIGH) RPi rail

# Note: GPIO.LOW  - 0V
#       GPIO.HIGH - 3.3V or 5V ???? (RPi rail voltage)


class DosimeterTimer(object):
    """
    Master object for dosimeter operation.

    Initializes Dosimeter, LEDs and DosimeterCommunicator,
    tracks time intervals, and converts the counts from Dosimeter into
    a CPM for DosimeterCommunicator to give to the buffers and the server.
    """

    pass


class Dosimeter(object):
    """
    Dosimeter takes counts from the sensor, flashing the LED and adding to a
    queue of counts.
    """

    pass


class LED(object):
    """
    Represents one LED, available for blinking or steady operation.
    """

    pass


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
