# -*- coding: utf-8 -*-

from __future__ import print_function

import unittest
import time

from globalvalues import RPI
if RPI:
    import RPi.GPIO as GPIO

import sensor
import sender
import auxiliaries
import manager

from globalvalues import POWER_LED_PIN, NETWORK_LED_PIN, COUNTS_LED_PIN
from globalvalues import ANSI_RESET, ANSI_GR, ANSI_RED


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
