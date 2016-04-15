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
        print('Testing set_verbosity()')

    def test_verbosity(self):
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
        print()


@unittest.skipUnless(RPI, "LED test only runs on a Raspberry Pi")
class TestLEDs(unittest.TestCase):

    def setUp(self):
        pins = (POWER_LED_PIN, NETWORK_LED_PIN, COUNTS_LED_PIN)
        self.LEDs = [auxiliaries.LED(pin=p) for p in pins]
        print('Testing LEDs',)

    def test_LED(self):
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

    def tearDown(self):
        GPIO.cleanup()
        print()


class TestNetworkStatus(unittest.TestCase):
    """
    Doesn't use the auto pinging subprocess - just manually run methods
    """

    good_hostname = 'www.google.com'
    bad_hostname = 'asnbdfmnasdbf.dosenet.dhcp.lbl.gov'

    def setUp(self):
        if RPI:
            self.LED = auxiliaries.LED(pin=NETWORK_LED_PIN)
        else:
            self.LED = None
        print('Testing NetworkStatus')

        self.net = auxiliaries.NetworkStatus(
            hostname=self.good_hostname,
            network_led=self.LED,
            pinging=False,
            verbosity=2)

    def test_is_up(self):
        self.net.update()
        self.assertTrue(self.net)

    def test_is_down(self):
        # give an invalid hostname
        self.net.hostname = self.bad_hostname
        self.net.update()

        self.assertFalse(self.net)

        self.net.hostname = self.good_hostname
        self.net.update()

    def tearDown(self):
        if RPI:
            GPIO.cleanup()
        del(self.net)
        print()


@unittest.skipUnless(
    RPI, "NetworkStatus live test only operates on a Raspberry Pi")
class TestNetworkStatusLive(TestNetworkStatus):
    """
    check the subprocess that pings at intervals
    also check LED behavior
    """

    # inherit good_hostname, bad_hostname
    # overwrite setUp(), tearDown(), test_is_up(), test_is_down()

    def setUp(self):
        self.LED = auxiliaries.LED(pin=NETWORK_LED_PIN)
        print('Testing NetworkStatus (live)')

        self.net = auxiliaries.NetworkStatus(
            hostname=self.good_hostname,
            up_interval_s=3,
            down_interval_s=1,
            network_led=self.LED,
            pinging=True,
            verbosity=2)

    def test_is_up(self):
        print('test_is_up (live)...')
        time.sleep(2)
        self.assertTrue(self.net)
        time.sleep(6)
        self.assertTrue(self.net)

    @unittest.skip(
        ("test_is_down (live) doesn't work until I can " +
         "hack the system network settings..."))
    def test_is_down(self):
        print('test_is_down (live)...')
        # give an invalid hostname
        self.net.hostname = self.bad_hostname

        time.sleep(3)
        self.assertFalse(self.net)
        time.sleep(3)

        # restore connection
        self.net.hostname = self.good_hostname

        time.sleep(1)
        self.assertTrue(self.net)
        time.sleep(3)
        self.assertTrue(self.net)

    def tearDown(self):
        self.net.stop_pinging()
        GPIO.cleanup()


class TestConfig(unittest.TestCase):
    # TODO
    pass


class TestPublicKey(unittest.TestCase):
    # TODO
    pass


class TestSensor(unittest.TestCase):

    def setUp(self):
        # fake sensor - only simulating counts
        self.sensor = sensor.Sensor(max_accumulation_time_s=2, use_gpio=False)

    def tearDown(self):
        self.sensor.cleanup()
        self.sensor = None

    def test_basic_counts(self):
        self.assertEqual(len(self.sensor.get_all_counts()), 0)
        n = 3
        [self.sensor.count() for _ in xrange(n)]
        self.assertEqual(len(self.sensor.get_all_counts()), n)

    def test_max_accum(self):
        self.assertEqual(len(self.sensor.get_all_counts()), 0)

        n1 = 3
        [self.sensor.count() for _ in xrange(n1)]
        self.assertEqual(len(self.sensor.get_all_counts()), n1)

        time.sleep(1)
        n2 = 4
        [self.sensor.count() for _ in xrange(n2)]
        self.assertEqual(len(self.sensor.get_all_counts()), n1 + n2)

        time.sleep(1.5)
        self.assertEqual(len(self.sensor.get_all_counts()), n2)

        time.sleep(1)
        self.assertEqual(len(self.sensor.get_all_counts()), 0)


if __name__ == '__main__':
    unittest.main()
