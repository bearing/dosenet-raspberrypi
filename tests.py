# -*- coding: utf-8 -*-

from __future__ import print_function

try:
    import RPi.GPIO as GPIO
    RPI = True
except ImportError:
    print('Not on a Raspberry Pi, proceeding anyway')
    RPI = False

import unittest
import time

import sensor
import sender
import auxiliaries
import manager

POWER_LED_PIN = 19
NETWORK_LED_PIN = 20
COUNTS_LED_PIN = 21

# ANSI color codes
ANSI_RESET = '\033[0m'
ANSI_BOLD = '\033[1m'
ANSI_YEL = '\033[33m' + ANSI_BOLD
ANSI_GR = '\033[32m' + ANSI_BOLD
ANSI_RED = '\033[31m' + ANSI_BOLD


class TestVerbosity(unittest.TestCase):

    class Verbosity1(object):
        def __init__(self, vlevel=1):
            auxiliaries.set_verbosity(self, verbosity=vlevel)

    def setUp(self):
        self.verbose_obj = TestVerbosity.Verbosity1(vlevel=1)

    def test_verbosity(self):

        print('Testing set_verbosity()')
        print('Two words of {}green text{} should appear here: '.format(
            ANSI_GR, ANSI_RESET))
        self.verbose_obj.vprint(0, '{}one{}'.format(ANSI_GR, ANSI_RESET))
        self.verbose_obj.vprint(1, '{}two{}'.format(ANSI_GR, ANSI_RESET))
        self.verbose_obj.vprint(2, '{}three{}'.format(ANSI_RED, ANSI_RESET))
        self.verbose_obj.vprint(3, '{}four{}'.format(ANSI_RED, ANSI_RESET))
        print()
        self.assertTrue(True)

    def tearDown(self):
        del(self.verbose_obj)


class TestLEDs(unittest.TestCase):

    def setUp(self):
        if RPI:
            pins = (POWER_LED_PIN, NETWORK_LED_PIN, COUNTS_LED_PIN)
            self.LEDs = [auxiliaries.LED(pin=p) for p in pins]

    def test_LED(self):
        if RPI:
            print('Testing LEDs',)

            print('on')
            [LED.on() for LED in self.LEDs]
            time.sleep(1)

            print('off')
            [LED.off() for LED in self.LEDs]
            time.sleep(1)

            print('flash')
            [LED.flash() for LED in self.LEDs]
            time.sleep(1)

            print('start blink')
            [LED.start_blink(interval=0.5) for LED in self.LEDs]
            time.sleep(3)

            print('stop blink')
            [LED.stop_blink() for LED in self.LEDs]
            time.sleep(1)
        else:
            print('Not on a Raspberry Pi - skipping LED tests')
            self.assertTrue(True)

    def tearDown(self):
        if RPI:
            GPIO.cleanup()


class TestNetworkStatus(unittest.TestCase):

    def setUp(self):
        if RPI:
            # self.LED = auxiliaries.LED(pin=)
            pass


class TestConfig(unittest.TestCase):
    # TODO
    pass


class TestPublicKey(unittest.TestCase):
    # TODO
    pass


if __name__ == '__main__':
    unittest.main()
