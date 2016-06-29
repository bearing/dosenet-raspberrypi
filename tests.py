# -*- coding: utf-8 -*-

from __future__ import print_function

import unittest
import time
import os
import csv

from globalvalues import RPI
if RPI:
    import RPi.GPIO as GPIO

import sensor
import sender
import auxiliaries
import cust_crypt

from auxiliaries import get_data
from manager import Manager

from globalvalues import POWER_LED_PIN, NETWORK_LED_PIN, COUNTS_LED_PIN
from globalvalues import DEFAULT_CONFIG, DEFAULT_PUBLICKEY
from globalvalues import ANSI_RESET, ANSI_GR, ANSI_RED

TEST_DATALOG = 'data-log-testfile.txt'

if RPI:
    test_config_path = DEFAULT_CONFIG
    test_publickey_path = DEFAULT_PUBLICKEY
    configs_present = True
else:
    # obviously, for security, the config and public key should NOT be
    #   included in the (public) repo!
    # these paths are for Brian's LBL desktop, but you could put them
    #   here for other machines too.
    test_config_path = './testconfig/config.csv'
    test_publickey_path = './testconfig/id_rsa_lbl.pub'
    if (os.path.exists(test_config_path) and
            os.path.exists(test_publickey_path)):
        print('Found config files')
        configs_present = True
    else:
        print('Config files not found!')
        configs_present = False

TEST_LOGFILE = 'test.log'


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


class TestLogging(unittest.TestCase):

    class Verbosity2(object):
        def __init__(self, vlevel=1, logfile=TEST_LOGFILE):
            try:
                os.remove(logfile)
            except OSError:
                pass
            auxiliaries.set_verbosity(self, verbosity=vlevel, logfile=logfile)

    def setUp(self):
        self.verbose_obj = TestLogging.Verbosity2(vlevel=1)
        print('Testing logging')

    def test_logging(self):
        print('Two words of {}green text{} should appear here: '.format(
            ANSI_GR, ANSI_RESET))
        textlines = [
            '{}one{}'.format(ANSI_GR, ANSI_RESET),
            '{}two{}'.format(ANSI_GR, ANSI_RESET),
            '{}three{}'.format(ANSI_RED, ANSI_RESET),
            '{}four{}'.format(ANSI_RED, ANSI_RESET)
        ]
        [self.verbose_obj.vprint(i, textlines[i]) for i in range(4)]
        print()
        with open(TEST_LOGFILE, 'r') as f:
            fline = f.readline()
            self.assertTrue(fline.endswith(textlines[0] + '\n'))
            fline = f.readline()
            self.assertTrue(fline.endswith(textlines[1] + '\n'))
            fline = f.readline()
            self.assertFalse(fline)

    def tearDown(self):
        del(self.verbose_obj)
        try:
            os.remove(TEST_LOGFILE)
        except OSError:
            pass
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


@unittest.skipUnless(configs_present, "Config test requires config files")
class TestConfig(unittest.TestCase):

    def test(self):
        config = auxiliaries.Config(test_config_path, verbosity=2)
        self.assertIsNotNone(config.ID)
        self.assertIsNotNone(config.hash)
        self.assertIsNotNone(config.lat)
        self.assertIsNotNone(config.long)


@unittest.skipUnless(configs_present, "PublicKey test requires config files")
class TestPublicKey(unittest.TestCase):

    def setUp(self):
        self.publickey = auxiliaries.PublicKey(
            test_publickey_path, verbosity=2)
        self.assertIsInstance(
            self.publickey.encrypter, cust_crypt.PublicDEncrypt)

    def test_encrypt(self):
        test_packet = 'This is a string with which we are testing encryption'
        encrypted_packet = self.publickey.encrypter.encrypt_message(
            test_packet)[0]
        self.assertIsInstance(encrypted_packet, str)


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


class TestSender(unittest.TestCase):

    def test_missing_config(self):
        ss = sender.ServerSender(
            manager=None,
            network_status=None,
            config=None,
            publickey=None,
            verbosity=4)
        with self.assertRaises(sender.MissingFile):
            ss.send_cpm(0, 0)

    @unittest.skipUnless(configs_present, "Sender tests require config files")
    def test_missing_publickey(self):
        ss = sender.ServerSender(
            manager=None,
            network_status=None,
            config=auxiliaries.Config(test_config_path),
            publickey=None,
            verbosity=4)
        with self.assertRaises(sender.MissingFile):
            ss.send_cpm(0, 0)

    @unittest.skipUnless(configs_present, "Test packets require config files")
    def test_send_test_udp(self):
        sender.send_test_packets(
            mode='udp',
            config=test_config_path,
            publickey=test_publickey_path,
            n=1)
        print(' ~ Check that the server received a test UDP packet ~')
        self.assertTrue(True)

    @unittest.skipUnless(configs_present, "Test packets require config files")
    def test_send_test_tcp(self):
        sender.send_test_packets(
            mode='tcp',
            config=test_config_path,
            publickey=test_publickey_path,
            n=1)
        print(' ~ Check that the server received a test TCP packet ~')
        self.assertTrue(True)


class TestDataLog(unittest.TestCase):

    def setUp(self):
        print('Checking local data')

    def test_get_data(self):
        """
        Checks the data log functionality.

        Creates a test data log, simulates 2 counts,
        checks that the test data log was created,
        checks that there are 2 counts, and then deletes the test datalog.
        """
        mgr = Manager(test=True, datalog=TEST_DATALOG)

        now = time.time()
        mgr.handle_cpm(now - 10, now)
        [mgr.sensor.count() for _ in xrange(2)]
        mgr.handle_cpm(now, now + 10)
        output = get_data(TEST_DATALOG)
        print(output)

        GPIO.cleanup()
        del(mgr)

        self.assertIsNotNone(output)
        self.assertEqual(len(output), 2)

    def tearDown(self):
        os.remove(TEST_DATALOG)
        print()


class DequeObject(unittest.TestCase):

    def setUp(self):
        print('Testing Deque Object')

    def test_no_network(self):
        """
        Creates a deque data structure, runs manager with no network,
        checks if deque was created, checks if cpm data was added to
        the deque object, checks if the Data_Handler class was
        created.
        """
        mgr = Manager(protocol='new')
        mgr.network_up = False

        now = time.time()
        mgr.handle_cpm(now - 10, now)
        [mgr.sensor.count() for _ in xrange(2)]
        mgr.handle_cpm(now, now + 10)

        self.assertIsNotNone(mgr.data_handler.queue)
        self.assertEqual(len(mgr.data_handler.queue), 2)
        self.assertIsNotNone(mgr.data_handler)

        GPIO.cleanup()
        del(mgr)

    def tearDown(self):
        print()


if __name__ == '__main__':
    unittest.main()
