from __future__ import print_function

import time
import argparse
import traceback
import signal
import sys
import csv
import os
import subprocess
import socket
try:
    import pika
except:
    pass
import json
try:
    import kromek
except:
    print("Not set up to run a D3S, continuing anyway")
try:
    import Adafruit_MCP3008
except:
    print("Not set up to run a CO2 sensor, continuing anyway")

import numpy as np
import datetime
from Crypto.Cipher import AES
from collections import deque

from globalvalues import RPI
if RPI:
    import RPi.GPIO as GPIO

from auxiliaries import LED, Config, PublicKey
from auxiliaries import datetime_from_epoch, set_verbosity
from sensor import Sensor
from sender import ServerSender
from data_handlers import Data_Handler_Pocket
from data_handlers import Data_Handler_D3S
from data_handlers import Data_Handler_AQ
from data_handlers import Data_Handler_CO2
from data_handlers import Data_Handler_Weather

from globalvalues import SIGNAL_PIN, NOISE_PIN, PIZERO_SIGNAL_PIN, NETWORK_LED_BLINK_PERIOD_S
from globalvalues import NEW_NETWORK_LED_PIN, OLD_NETWORK_LED_PIN
from globalvalues import NEW_COUNTS_LED_PIN, OLD_COUNTS_LED_PIN
from globalvalues import NEW_D3S_LED_PIN, OLD_D3S_LED_PIN
from globalvalues import D3S_LED_BLINK_PERIOD_INITIAL, D3S_LED_BLINK_PERIOD_DEVICE_FOUND

from globalvalues import NEW_SENSOR_DISPLAY_TEXT, OLD_SENSOR_DISPLAY_TEXT
from globalvalues import OLED_CONNECTED_TEXT, SINGLE_BREAK_LINE
from globalvalues import RUNNING_DISPLAY_TEXT, SENSOR_NAMES, DATA_NAMES
from globalvalues import DEFAULT_CONFIG, DEFAULT_PUBLICKEY, DEFAULT_AESKEY
from globalvalues import DEFAULT_LOGFILES, DEFAULT_DATALOGS
from globalvalues import DEFAULT_HOSTNAME, DEFAULT_UDP_PORT, DEFAULT_TCP_PORT
from globalvalues import DEFAULT_SENDER_MODE
from globalvalues import DEFAULT_CALIBRATIONLOG_D3S, DEFAULT_CALIBRATIONLOG_TIME, DEFAULT_D3STEST_TIME
from globalvalues import DEFAULT_INTERVALS, DEFAULT_TEST_INTERVALS, TEST_INTERVAL_NAMES
from globalvalues import AQ_VARIABLES, CO2_VARIABLES
from globalvalues import WEATHER_VARIABLES, WEATHER_VARIABLES_UNITS
#from globalvalues import DEFAULT_OLED_LOGS
try:
    from globalvalues import DEFAULT_WEATHER_PORT
except ImportError:
    pass
try:
    from globalvalues import DEFAULT_AQ_PORT
except ImportError:
    pass
from globalvalues import CO2_pins
"""
try:
    from globalvalues import DEFAULT_CO2_PORT
except:
    pass
"""
from globalvalues import REBOOT_SCRIPT, GIT_DIRECTORY, BOOT_LOG_CODE
from globalvalues import strf
from globalvalues import ANSI_RED, ANSI_RESET

def signal_term_handler(signal, frame):
    # If SIGTERM signal is intercepted, the SystemExit exception routines
    #   get run
    sys.exit(0)

#signal.signal(signal.SIGTERM, signal_term_handler)

def signal_quit_handler(signal, frame):
    # If SIGQUIT signal is intercepted, the SystemExit exception routines
    #   get run if it's right after an interval
    mgr.quit_after_interval = True

def timeout_handler(num, stack):
    raise Exception("TIMEOUT")

signal.signal(signal.SIGALRM, timeout_handler)

signal.signal(signal.SIGQUIT, signal_quit_handler)

class Base_Manager(object):
    """
    Main Manager class that contains the general functions for any
    of the connected detectors or sensors.

    The specific functions are handled in the sub classes below this class.
    """
    def __init__(self,
                 interval=None,
                 config=None,
                 publickey=None,
                 hostname=DEFAULT_HOSTNAME,
                 port=None,
                 test=None,
                 verbosity=None,
                 log=False,
                 logfile=None,
                 datalog=None,
                 datalogflag=False,
                 sender_mode=DEFAULT_SENDER_MODE,
                 aeskey=None,
                 sensor_type=None,
                 new_setup=None,
                 sensor=None,
                 sensor_names=SENSOR_NAMES,
                 data_names=DATA_NAMES,
                 cirtest=False,
                 oled=False,
                 oled_log=None,
                 oled_test=False,
                 small_board=False,
                 ):
        self.new_setup = new_setup
        self.sensor_type = sensor_type

        self.datalog = datalog
        self.datalogflag = datalogflag

        self.oled = oled
        self.oled_log = oled_log

        self.test = test
        self.oled_test = oled_test

        self.small_board = small_board

        # Replacing the original d_flag and f_flag functions for
        if self.datalogflag or self.test:
            if self.datalog is None:
                for i in range(len(DEFAULT_DATALOGS)):
                    if self.sensor_type == i+1:
                        self.datalog = DEFAULT_DATALOGS[i]
                        break
        if self.datalog:
            self.datalogflag = True

        if self.oled_test:
            self.oled = True

        self.make_data_log(self.datalog)

        self.data_names = data_names

        self.cirtest = cirtest

        self.handle_input(log, logfile, verbosity,
                          test, interval, config, publickey, aeskey)

        self.sender_mode = sender_mode
        self.port = port

        self.sensor_names = sensor_names

    def make_data_log(self, file):
        if self.datalogflag:
            with open(file, 'a') as f:
                pass
    def make_oled_log(self, file):
        """
        Works the same as make_data_log but is separate
        so that the oled_log isn't created when data logging is on
        but an OLED screen is not connected.
        """
        if self.oled:
            with open(file, 'a') as f:
                pass

    def handle_input(self, log, logfile, verbosity,
                         test, interval, config, publickey, aeskey):

        if verbosity is None:
            if test:
                verbosity = 3
            else:
                verbosity = 1
            if self.cirtest:
                verbosity = 0
        self.v = verbosity

        if log:
            if logfile is None:
                if self.sensor_type > 5 or self.sensor_type < 1:
                    print("No sensor running, try running through one of the subclasses to get a proper setup.")
                    self.takedown()
                for i in range(len(DEFAULT_LOGFILES)):
                    if self.sensor_type == i+1:
                        logfile = DEFAULT_LOGFILES[i]
                        break
            self.logfile = logfile
        else:
            self.logfile = None

        set_verbosity(self, logfile=logfile)

        if log:
            self.vprint(1, '')
            self.vprint(1, 'Writing to logfile at {}'.format(self.logfile))
        self.running = True

        if self.test or self.oled_test:
            if interval is None:
                for i in range(len(DEFAULT_TEST_INTERVALS)):
                    if self.sensor_type == i+1:
                        self.vprint(
                            2, "No interval given, using default for {}".format(TEST_INTERVAL_NAMES[i]))
                        interval = DEFAULT_TEST_INTERVALS[i]
                        break

        if interval is None:
            for i in range(len(DEFAULT_INTERVALS)):
                if self.sensor_type == i+1:
                    self.vprint(
                        2, "No interval given, using interval at 5 minutes")
                    interval = DEFAULT_INTERVALS[i]
                    break

        if config is None:
            self.vprint(2, "No config file given, " +
                        "attempting to use default config path")
            config = DEFAULT_CONFIG
        if publickey is None:
            self.vprint(2, "No publickey file given, " +
                        "attempting to use default publickey path")
            publickey = DEFAULT_PUBLICKEY
        if aeskey is None and self.sensor_type == 2:
            #Only set the AES key when the D3S is being used
            self.vprint(2, "No AES key file given, " +
                        "attempting to use default AES key path")
            aeskey = DEFAULT_AESKEY

        self.interval = interval

        if config and not self.test and not self.cirtest:
            try:
                self.config = Config(config,
                                     verbosity=self.v, logfile=self.logfile)
                if self.new_setup == None:
                    self.int_ID = int(self.config.ID)
                    if self.int_ID == 5 or self.int_ID == 29 or self.int_ID == 32 or \
                        self.int_ID == 33 or self.int_ID >= 39:
                        self.new_setup = True
                    else:
                        self.new_setup = False
            except IOError:
                raise IOError(
                    'Unable to open config file {}!'.format(config))
        else:
            self.vprint(
                1, 'WARNING: no config file given. Not posting to server')
            self.config = None
            self.new_setup = True

        if publickey:
            try:
                self.publickey = PublicKey(
                    publickey, verbosity=self.v, logfile=self.logfile)
            except IOError:
                raise IOError(
                    'Unable to load publickey file {}!'.format(publickey))
        else:
            self.vprint(
                1, 'WARNING: no public key given. Not posting to server')
            self.publickey = None

        if aeskey:
            try:
                with open(aeskey, 'r') as aesfile:
                    key = aesfile.read()
                    self.aes = AES.new(key, mode=AES.MODE_ECB)
            except IOError:
                raise IOError('Unable to load AES key file {}!'.format(
                    aeskey))
        if not aeskey and self.sensor_type == 2:
            self.vprint(
                1, 'WARNING: no AES key given. Not posting to server')
            self.aes = None
        if self.sensor_type != 2:
            self.aes = None

    def run(self):
        """
        Main method to run the sensors continuously, the run
        procedure is determined by the sensor_type of the instance.
        """
        if self.oled:
            self.vprint(1, SINGLE_BREAK_LINE)
            self.vprint(
                    1, OLED_CONNECTED_TEXT)
            self.vprint(1, SINGLE_BREAK_LINE)

        if self.new_setup:
            self.vprint(
                    1, NEW_SENSOR_DISPLAY_TEXT.format(sensor_name=self.sensor_names[self.sensor_type-1]))
        else:
            self.vprint(
                    1, OLD_SENSOR_DISPLAY_TEXT.format(sensor_name=self.sensor_names[self.sensor_type-1]))
        this_start, this_end = self.get_interval(time.time())
        if self.sensor_type != 2:
            self.vprint(
                1, RUNNING_DISPLAY_TEXT.format(
                    start_time=datetime_from_epoch(this_start).strftime(strf),
                    date=str(datetime.date.today()),
                    interval=self.interval))
        self.running = True

        if self.sensor_type == 1:
            try:
                while self.running:
                    self.vprint(3, 'Sleeping at {} until {}'.format(
                        datetime_from_epoch(time.time()),
                        datetime_from_epoch(this_end)))
                    try:
                        self.sleep_until(this_end)
                    except SleepError:
                        self.vprint(1, 'SleepError: system clock skipped ahead!')
                        self.vprint(
                            3, 'former this_start = {}, this_end = {}'.format(
                                datetime_from_epoch(this_start),
                                datetime_from_epoch(this_end)))
                        this_start, this_end = self.get_interval(
                            time.time() - self.interval)

                    self.handle_data(this_start, this_end, None)
                    if self.quit_after_interval:
                        self.vprint(1, 'Reboot: taking down Manager')
                        self.stop()
                        self.takedown()
                        os.system('sudo {0} {1}'.format(
                            REBOOT_SCRIPT, self.branch))
                    this_start, this_end = self.get_interval(this_end)
            except KeyboardInterrupt:
                self.vprint(1, '\nKeyboardInterrupt: stopping Manager run')
                self.stop()
                self.takedown()
            except SystemExit:
                self.vprint(1, '\nSystemExit: taking down Manager')
                self.stop()
                self.takedown()

        if self.sensor_type == 2:
            print("Attempting to connect to D3S now")

            if self.transport == 'any':
                devs = kromek.discover()
            else:
                devs = kromek.discover(self.transport)

            if len(devs) <= 0:
                print("No D3S connected, exiting manager now")
                if not self.small_board:
                    self.d3s_LED.stop_blink()
                self.d3s_presence = False
                GPIO.cleanup()
                return
            else:
                print ('Discovered %s' % devs)
                print("D3S device found, checking for data now")
                if not self.small_board:
                    self.d3s_LED.start_blink(interval=self.d3s_LED_blink_period_2)
                self.d3s_presence = True
            filtered = []

            for dev in devs:
                if self.device == 'all' or dev[0] in self.device:
                    filtered.append(dev)

            devs = filtered
            if len(devs) <= 0:
                print("No D3S connected, exiting manager now")
                if not self.small_board:
                    self.d3s_LED.stop_blink()
                self.d3s_presence = False
                GPIO.cleanup()
                return

            signal.alarm(10)
            # Checks if the RaspberryPi is getting data from the D3S and turns on
            # the red LED if it is. If a D3S is connected but no data is being recieved,
            # it tries a couple times then reboots the RaspberryPi.
            if self.d3s_presence:
                try:
                    test_time_outer = time.time() + self.signal_test_time + 25
                    while time.time() < test_time_outer:
                        test_time_inner = time.time() + self.signal_test_time + 5
                        while time.time() < test_time_inner:
                            try:
                                with kromek.Controller(devs, self.signal_test_time) as controller:
                                    for reading in controller.read():
                                        if sum(reading[4]) != 0:
                                            self.d3s_light_switch = True
                                            signal.alarm(0)
                                            break
                                        else:
                                            break
                            except Exception as e:
                                print(e)
                                print("Data acquisition attempt {} failed".format(self.d3s_data_attempts))
                                if self.d3s_data_attempts != self.d3s_data_lim:
                                    signal.alarm(10)
                                self.d3s_data_attempts += 1
                        if self.d3s_light_switch:
                            print("Data from D3S found on attempt {}".format(self.d3s_data_attempts))
                            break
                        if self.d3s_data_attempts > self.d3s_data_lim:
                            print("Failed to find data from D3S {} times".format(self.d3s_data_attempts-1))
                            print("The D3S is either having data collection issues or is currently off")
                            self.d3s_presence = False
                            break
                except KeyboardInterrupt:
                    self.vprint(1, '\nKeyboardInterrupt: stopping Manager run')
                    self.takedown()
                except SystemExit:
                    self.vprint(1, '\nSystemExit: taking down Manager')
                    self.takedown()

            if self.d3s_light_switch:
                if not self.small_board:
                    self.d3s_LED.stop_blink()
                print("D3S data connection found, continuing with normal data collection")
                if not self.small_board:
                    self.d3s_LED.on()
            else:
                if not self.small_board:
                    self.d3s_LED.stop_blink()
                print("Turning off light and will try to gather data again at reboot")
                if not self.small_board:
                    self.d3s_LED.off()
                    GPIO.cleanup()
                return

            if self.d3s_presence:
                self.vprint(
                    1, RUNNING_DISPLAY_TEXT.format(
                        start_time=datetime_from_epoch(this_start).strftime(strf),
                        date=str(datetime.date.today()),
                        interval=self.interval))

                done_devices = set()
                try:
                    while self.running:
                        with kromek.Controller(devs, self.interval) as controller:
                            for reading in controller.read():
                                if self.create_structures:
                                    self.total = np.array(reading[4])
                                    self.lst = np.array([reading[4]])
                                    self.create_structures = False
                                else:
                                    self.total += np.array(reading[4])
                                    self.lst = np.concatenate(
                                        (self.lst, [np.array(reading[4])]))
                                serial = reading[0]
                                dev_count = reading[1]
                                if serial not in done_devices:
                                    this_start, this_end = self.get_interval(
                                        time.time() - self.interval)

                                    self.handle_data(
                                        this_start, this_end, reading[4])

                                if dev_count >= self.count > 0:
                                    done_devices.add(serial)
                                    controller.stop_collector(serial)
                                if len(done_devices) >= len(devs):
                                    break
                except KeyboardInterrupt:
                    self.vprint(1, '\nKeyboardInterrupt: stopping Manager run')
                    self.takedown()
                except SystemExit:
                    self.vprint(1, '\nSystemExit: taking down Manager')
                    self.takedown()

        if self.sensor_type == 3 or self.sensor_type == 4 or self.sensor_type == 5:
            try:
                while self.running:
                    self.handle_data(this_start, this_end, None)
                    this_start, this_end = self.get_interval(this_end)
            except KeyboardInterrupt:
                self.vprint(1, '\nKeyboardInterrupt: stopping Manager run')
                self.stop()
                self.takedown()
            except SystemExit:
                self.vprint(1, '\nSystemExit: taking down Manager')
                self.stop()
                self.takedown()

    def get_interval(self, start_time):
        """
        Return start and end time for interval, based on given start_time.
        """
        end_time = start_time + self.interval
        return start_time, end_time

    def stop(self):
        """Stop counting time."""
        self.running = False

    def data_log(self, file, **kwargs):
        """
        Writes measured data to the file.
        """
        time_string = time.strftime("%Y-%m-%d %H:%M:%S")
        if self.sensor_type == 1:
            cpm, cpm_err = kwargs.get('cpm'), kwargs.get('cpm_err')
            if self.datalogflag:
                with open(file, 'a') as f:
                    f.write('{0}, {1}, {2}'.format(time_string, cpm, cpm_err))
                    f.write('\n')
                    self.vprint(2, 'Writing CPM to data log at {}'.format(file))
        if self.sensor_type == 2:
            spectra = kwargs.get('spectra')
            if self.datalogflag:
                with open(file, 'a') as f:
                    f.write('{0}, '.format(spectra))
                    self.vprint(
                        2, 'Writing spectra to data log at {}'.format(file))
        if self.sensor_type == 3 or self.sensor_type == 4 or self.sensor_type == 5:
            average_data = kwargs.get('average_data')
            if self.datalogflag:
                with open(file, 'a') as f:
                    f.write('{0}, {1}'.format(time_string, average_data))
                    f.write('\n')
                    self.vprint(2, 'Writing average {} to data log at {}'.format(self.data_names[self.sensor_type-1],file))

    def oled_send(self, data):
        """
        Sends data to the RabbitMQ queue 'toOLED' which is being
        read by the OLED_Manager instance and displayed to a connected screen.
        """
        connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
        channel = connection.channel()
        channel.queue_declare(queue='toOLED')
        message = {'id': self.sensor_type, 'data': data}
        self.vprint(1, message)
        channel.basic_publish(exchange='',routing_key='toOLED',body=json.dumps(message))
        connection.close()

    def oled_receive(self):
        """
        Undefined for now but might be useful in the future for logging?
        """
        pass

    def handle_data(self, this_start, this_end, spectra):
        """
        Chooses the type of sensor that is being used and
        determines the data handling type to use.
        """
        average_data, sensor_data_set = [], []
        if self.sensor_type == 1:
            cpm, cpm_err = self.sensor.get_cpm(this_start, this_end)
            counts = int(round(cpm * self.interval / 60))

        if self.sensor_type == 3:
            while time.time() < this_end:
                text = self.AQ_port.read(32)
                buffer = [ord(c) for c in text]
                if buffer[0] == 66:
                    summation = sum(buffer[0:30])
                    checkbyte = (buffer[30]<<8)+buffer[31]
                    if summation == checkbyte:
                        current_second_data = []
                        buf = buffer[1:32]
                        for n in range(1,4):
                            current_second_data.append(repr(((buf[(2*n)+1]<<8) + buf[(2*n)+2])))
                        for n in range(1,7):
                            current_second_data.append(repr(((buf[(2*n)+13]<<8) + buf[(2*n)+14])))
                        current_second_data = ['%.2f' % i for i in list(map(float, current_second_data))]
                        current_second_data.insert(0,datetime.datetime.now())
                        sensor_data_set.append(current_second_data)
            for c in range(len(self.variables)):
                c_data = []
                for i in range(len(sensor_data_set)):
                    c_data.append(sensor_data_set[i][c+1])
                c_data_int = list(map(float, c_data))
                avg_f = sum(c_data_int)/len(c_data_int)
                avg_c = float('%.2f'%avg_f)
                average_data.append(avg_c)

        if self.sensor_type == 4:
            while time.time() < this_end:
                date_time = datetime.datetime.now()
                this_instant_data = []
                values = [0]*8
                for i in range(8):
                    values[i] = self.CO2_port.read_adc(i)
                conc = 5000/496*values[0] - 1250
                uv_index = values[7]
                this_instant_data.append(date_time)
                this_instant_data.append(float('%.2f'%conc))
                this_instant_data.append(float('%.2f'%uv_index))
                sensor_data_set.append(this_instant_data)
            for c in range(len(self.variables)):
                c_data = []
                for i in range(len(sensor_data_set)):
                    c_data.append(sensor_data_set[i][c+1])
                c_data_int = list(map(float, c_data))
                avg_f = sum(c_data_int)/len(c_data_int)
                avg_c = float('%.2f'%avg_f)
                average_data.append(avg_c)

        if self.sensor_type == 5:
            while time.time() < this_end:
                date_time = datetime.datetime.now()
                this_instant_data = []
                temp = self.Weather_Port.read_temperature()
                press = self.Weather_Port.read_pressure() / 100
                humid = self.Weather_Port.read_humidity()
                this_instant_data.append(date_time)
                this_instant_data.append(float('%.2f'%temp))
                this_instant_data.append(float('%.2f'%press))
                this_instant_data.append(float('%.2f'%humid))
                sensor_data_set.append(this_instant_data)
            for c in range(len(self.variables)):
                c_data = []
                for i in range(len(sensor_data_set)):
                    c_data.append(sensor_data_set[i][c+1])
                c_data_int = list(map(float, c_data))
                avg_f = sum(c_data_int)/len(c_data_int)
                avg_c = float('%.2f'%avg_f)
                average_data.append(avg_c)

        if not self.cirtest:
            if self.sensor_type == 1:
                self.data_handler.main(
                    self.datalog, this_start, this_end,
                    cpm=cpm, cpm_err=cpm_err, counts=counts)
            elif self.sensor_type == 2:
                self.data_handler.main(
                    self.datalog, this_start, this_end,
                    calibrationlog=self.calibrationlog, spectra=spectra)
            elif self.sensor_type in [3,4,5]:
                self.data_handler.main(
                    self.datalog, this_start, this_end, average_data=average_data)
        else:
            if self.sensor_type == 1:
                self.data_log(self.datalog, cpm=cpm, cpm_err=cpm_err)
                return counts, cpm, cpm_err
            elif self.sensor_type in [3,4,5]:
                self.data_log(self.datalog, average_data=average_data)
                return average_data

    def takedown(self):
        """
        Shuts down any sensors or lights and runs unique procedures for
        individual sensors. Then cleans up GPiO for clean restart procedure and
        deletes itself.
        """

        #Unique shutdown procedure for Pocket Geiger
        if self.sensor_type == 1:
            #if not self.small_board:
            self.sensor.cleanup()
            del(self.sensor)

        #Unique shutdown procedure for D3S
        if self.sensor_type == 2:
            self.running = False
            try:
                self.d3s_LED.off()
            except AttributeError:
                pass


        if self.sensor_type != 3:
            if not self.small_board:
                try:
                    GPIO.cleanup()
                except NameError:
                    pass
            else:
                pass


        self.data_handler.send_all_to_backlog()

        del(self)

class Manager_Pocket(Base_Manager):
    """
    The subclass that uses the main Manager class and initializes the
    pocket geiger sensor.
    """
    def __init__(self,
                 counts_LED_pin=None,
                 network_LED_pin=None,
                 noise_pin=NOISE_PIN,
                 signal_pin=None,
                 **kwargs):

        super(Manager_Pocket, self).__init__(sensor_type=1, **kwargs)

        self.quit_after_interval = False

        if not signal_pin:
            if self.small_board:
                signal_pin=PIZERO_SIGNAL_PIN
            else:
                signal_pin=SIGNAL_PIN

        if RPI:
            if not self.small_board:
                if counts_LED_pin == None:
                    if self.new_setup:
                        self.counts_LED = LED(NEW_COUNTS_LED_PIN)
                    else:
                        self.counts_LED = LED(OLD_COUNTS_LED_PIN)
                else:
                    self.counts_LED = LED(counts_LED_pin)
                if network_LED_pin == None:
                    if self.new_setup:
                        self.network_LED = LED(NEW_NETWORK_LED_PIN)
                    else:
                        self.network_LED = LED(OLD_NETWORK_LED_PIN)
                else:
                    self.network_LED = LED(network_LED_pin)
            else:
                self.counts_LED = None
                self.network_LED = None
        else:
            self.counts_LED = None
            self.network_LED = None

        self.sensor = Sensor(
            counts_LED=self.counts_LED,
            verbosity=self.v,
            logfile=self.logfile,
            signal_pin=signal_pin)
        self.data_handler = Data_Handler_Pocket(
            manager=self,
            verbosity=self.v,
            logfile=self.logfile,
            network_led=self.network_LED)
        self.sender = ServerSender(
            manager=self,
            mode=self.sender_mode,
            port=self.port,
            verbosity=self.v,
            logfile=self.logfile)

        self.init_log()
        self.branch = ''

        self.data_handler.backlog_to_queue()

    def init_log(self):
        """
        Post log message to server regarding Manager startup.
        """

        # set working directory
        cwd = os.getcwd()
        os.chdir(GIT_DIRECTORY)

        branch = subprocess.check_output(
            ['git', 'rev-parse', '--abbrev-ref', 'HEAD']).rstrip()
        self.vprint(3, 'Found git branch: {}'.format(branch))
        commit = subprocess.check_output(
            ['git', 'rev-parse', '--short', 'HEAD']).rstrip()
        self.vprint(3, 'Found commit: {}'.format(commit))

        os.chdir(cwd)

        msg_code = BOOT_LOG_CODE
        msg_text = 'Booting on {} at {}'.format(branch, commit)
        self.vprint(1, 'Sending log message: [{}] {}'.format(
            msg_code, msg_text))
        try:
            self.sender.send_log(msg_code, msg_text)
        except (socket.gaierror, socket.error, socket.timeout):
            self.vprint(1, 'Failed to send log message, network error')
            if self.network_LED:
                self.network_LED.start_blink(
                    interval=NETWORK_LED_BLINK_PERIOD_S)
        else:
            self.vprint(2, 'Success sending log message')
            if self.network_LED:
                if self.network_LED.blinker:
                    self.network_LED.stop_blink()
                self.network_LED.on()

    def sleep_until(self, end_time, retry=True):
        """
        Sleep until the given timestamp.

        Input:

          end_time: number of seconds since epoch, e.g. time.time()
        """

        catching_up_flag = False
        sleeptime = end_time - time.time()
        self.vprint(3, 'Sleeping for {} seconds'.format(sleeptime))
        if sleeptime < 0:
            # can happen if flushing queue to server takes longer than interval
            sleeptime = 0
            catching_up_flag = True
        time.sleep(sleeptime)
        if self.quit_after_interval and retry:
            # SIGQUIT signal somehow interrupts time.sleep
            # which makes the retry argument needed
            self.sleep_until(end_time, retry=False)
        now = time.time()
        self.vprint(
            2, 'sleep_until offset is {} seconds'.format(now - end_time))
        # normally this offset is < 0.1 s
        # although a reboot normally produces an offset of 9.5 s
        #   on the first cycle
        if not catching_up_flag and (now - end_time > 10 or now < end_time):
            # raspberry pi clock reset during this interval
            # normally the first half of the condition triggers it.
            raise SleepError

class Manager_D3S(Base_Manager):
    """
    The subclass that uses the main Manager class and initializes the D3S.
    """
    def __init__(self,
                 calibrationlog=None,
                 calibrationlogflag=False,
                 calibrationlogtime=None,
                 count=0,
                 d3s_LED_pin=None,
                 d3s_LED_blink=True,
                 d3s_LED_blink_period_1=D3S_LED_BLINK_PERIOD_INITIAL,
                 d3s_LED_blink_period_2=D3S_LED_BLINK_PERIOD_DEVICE_FOUND,
                 d3s_light_switch=False,
                 device='all',
                 log_bytes=False,
                 running=False,
                 signal_test_time=DEFAULT_D3STEST_TIME,
                 transport='usb',
                 d3s_presence=None,
                 d3s_data_attempts=1,
                 d3s_data_lim=3,
                 **kwargs):

        super(Manager_D3S, self).__init__(sensor_type=2, **kwargs)

        self.running = running

        self.total = None
        self.lst = None
        self.create_structures = True

        self.count = count

        self.transport = transport
        self.device = device
        self.log_bytes = log_bytes

        self.calibrationlog = calibrationlog
        self.calibrationlogflag = calibrationlogflag
        self.c_timer = 0
        self.calibrationlogtime = calibrationlogtime

        self.z_flag()
        self.j_flag()
        self.x_flag()
        self.make_calibration_log(self.calibrationlog)

        self.signal_test_time = signal_test_time
        self.d3s_presence = d3s_presence
        self.d3s_data_attempts = d3s_data_attempts
        self.d3s_data_lim = d3s_data_lim

        if not self.small_board:
            if d3s_LED_pin == None:
                if self.new_setup:
                    self.d3s_LED = LED(NEW_D3S_LED_PIN)
                else:
                    self.d3s_LED = LED(OLD_D3S_LED_PIN)
            else:
                self.d3s_LED = LED(d3s_LED_pin)

            self.d3s_light_switch = d3s_light_switch
            self.d3s_LED_blink_period_1 = d3s_LED_blink_period_1
            self.d3s_LED_blink_period_2 = d3s_LED_blink_period_2
            self.d3s_LED_blink = d3s_LED_blink

            if d3s_LED_blink:
                self.d3s_LED.start_blink(interval=self.d3s_LED_blink_period_1)
            if d3s_light_switch:
                self.d3s_LED.on()

        self.data_handler = Data_Handler_D3S(
            manager=self,
            verbosity=self.v,
            logfile=self.logfile,)
        self.sender = ServerSender(
            manager=self,
            mode=self.sender_mode,
            port=self.port,
            verbosity=self.v,
            logfile=self.logfile,)

        self.data_handler.backlog_to_queue()

    def z_flag(self):
        """
        Checks if the -z from_argparse is called.
        If it is called, sets the path of the calibration-log to
        DEFAULT_CALIBRATIONLOG_D3S.
        """
        if self.calibrationlogflag:
            self.calibrationlog = DEFAULT_CALIBRATIONLOG_D3S

    def j_flag(self):
        """
        Checks if the -j from_argparse is called.
        If it is called, sets calibrationlogflag to True.
        Also sets calibrationlogtime to DEFAULT_CALIBRATIONLOG_TIME.
        """
        if self.calibrationlog:
            self.calibrationlogflag = True
            self.calibrationlogtime = DEFAULT_CALIBRATIONLOG_TIME

    def x_flag(self):
        """
        Checks if -x is called.
        If it is called, sets calibrationlogflag to True.
        Also sets calibrationlog to DEFAULT_CALIBRATIONLOG_D3S.
        """
        if self.calibrationlogtime and (
                self.calibrationlogtime != DEFAULT_CALIBRATIONLOG_TIME):
            self.calibrationlog = DEFAULT_CALIBRATIONLOG_D3S
            self.calibrationlogflag = True

    def make_calibration_log(self, file):
        if self.calibrationlogflag:
            with open(file, 'a') as f:
                pass

    def calibration_log(self, file, spectra):
        """
        Writes spectra to calibration-log.
        """
        if self.calibrationlogflag:
            with open(file, 'a') as f:
                f.write('{0}, '.format(spectra))
                self.vprint(
                    2, 'Writing spectra to calibration log at {}'.format(file))
            self.c_timer += self.interval
            if self.c_timer >= self.calibrationlogtime:
                self.vprint(1, 'Calibration Complete')
                self.takedown()

class Manager_AQ(Base_Manager):
    """
    The subclass that uses the main Manager class and initializes the
    Air Quality sensor.
    """
    def __init__(self,
                 AQ_port=None,
                 variables=AQ_VARIABLES,
                 **kwargs):

        self.variables = variables

        super(Manager_AQ, self).__init__(sensor_type=3, **kwargs)

        if not AQ_port:
            self.AQ_port = DEFAULT_AQ_PORT
        else:
            self.AQ_port = AQ_port

        self.data_handler = Data_Handler_AQ(
            manager=self,
            verbosity=self.v,
            logfile=self.logfile,
            variables=self.variables)
        self.sender = ServerSender(
            manager=self,
            mode=self.sender_mode,
            port=self.port,
            verbosity=self.v,
            logfile=self.logfile)

        self.data_handler.backlog_to_queue()

class Manager_CO2(Base_Manager):
    """
    The subclass that uses the main Manager class and initializes the
    CO2 sensor.
    """
    def __init__(self,
                 CO2_port=None,
                 variables=CO2_VARIABLES,
                 **kwargs):

        self.variables = variables

        super(Manager_CO2, self).__init__(sensor_type=4, **kwargs)

        try:
            if not CO2_port:
                if self.small_board:
                    #GPIO.setwarnings(False)
                    #GPIO.setmode(GPIO.BCM)
                    #GPIO.setup(20,GPIO.IN)
                    #GPIO.setup(21,GPIO.IN)
                    self.CO2_port = Adafruit_MCP3008.MCP3008(clk=CO2_pins[1][0], cs=CO2_pins[1][1], miso=CO2_pins[1][2], mosi=CO2_pins[1][3])
                else:
                    self.CO2_port = Adafruit_MCP3008.MCP3008(clk=CO2_pins[0][0], cs=CO2_pins[0][1], miso=CO2_pins[0][2], mosi=CO2_pins[0][3])
            else:
                self.CO2_port = CO2_port
        except:
            print("Unable to import a CO2 port")

        self.data_handler = Data_Handler_CO2(
            manager=self,
            verbosity=self.v,
            logfile=self.logfile,
            variables=self.variables)
        self.sender = ServerSender(
            manager=self,
            mode=self.sender_mode,
            port=self.port,
            verbosity=self.v,
            logfile=self.logfile)

        self.data_handler.backlog_to_queue()

class Manager_Weather(Base_Manager):
    """
    The subclass that uses the main Manager class and initializes the
    weather sensor.
    """
    def __init__(self,
                 Weather_Port=None,
                 variables=WEATHER_VARIABLES,
                 variables_units=WEATHER_VARIABLES_UNITS,
                 **kwargs):

        self.variables = variables
        self.variables_units = variables_units

        super(Manager_Weather, self).__init__(sensor_type=5, **kwargs)

        if not Weather_Port:
            self.Weather_Port = DEFAULT_WEATHER_PORT
        else:
            self.Weather_Port = Weather_Port

        self.data_handler = Data_Handler_Weather(
            manager=self,
            verbosity=self.v,
            logfile=self.logfile,
            variables=self.variables,
            variables_units=self.variables_units)
        self.sender = ServerSender(
            manager=self,
            mode=self.sender_mode,
            port=self.port,
            verbosity=self.v,
            logfile=self.logfile)

        self.data_handler.backlog_to_queue()

class SleepError(Exception):
    pass

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--sensor', '-s', type=str, help='Enter a number corresponding ' +
        'to the sensor type where: \n1 = The Pocket Geiger \n2 = The D3S' +
        '\n3 = The Air Quality Sensor \n4 = The C02 Sensor')
    sensor = parser.parse_known_args()[0].sensor
    valid_sensors = [['POCKET_GEIGER', 'PG', '1'], ['D3S', '2'], ['AIR_QUALITY', 'AQ', '3'], ['CO2', '4'], ['WEATHER_SENSOR', 'WEATHER', '5']]
    for i, val in enumerate(valid_sensors):
        if not isinstance(sensor, int):
            if sensor.upper() in val:
                sensor = i+1
    if isinstance(sensor, str):
        print('{red}"{value}" is not a valid sensor choice, try entering any #1-5 or a sensor name{reset}'.format(
            red=ANSI_RED, value=sensor, reset=ANSI_RESET))
        sys.exit()

    #Generic Manager control variables.
    parser.add_argument(
        '--interval', '-i', type=int, default=None,
        help=('Interval of CPM measurement, in seconds' +
              ' (default 300 for normal mode)'))
    parser.add_argument(
        '--config', '-c', default=None,
        help='Specify a config file (default {})'.format(DEFAULT_CONFIG))
    parser.add_argument(
        '--publickey', '-k', default=None,
        help='Specify a publickey file (default {})'.format(
            DEFAULT_PUBLICKEY))
    parser.add_argument(
        '--hostname', '-5', default=DEFAULT_HOSTNAME,
        help='Specify a server hostname (default {})'.format(
            DEFAULT_HOSTNAME))
    parser.add_argument(
        '--port', '-p', type=int, default=None,
        help='Specify a port for the server ' +
        '(default {} for UDP, {} for TCP)'.format(
            DEFAULT_UDP_PORT, DEFAULT_TCP_PORT))
    parser.add_argument(
        '--test', '-t', action='store_true', default=False,
        help='Start in test mode (no config, 30s intervals)')
    parser.add_argument(
        '--oled_test', '-w', action='store_true', default=False,
        help='Mode used for testing the oled screen (30s intervals)')
    parser.add_argument(
        '--verbosity', '-v', type=int, default=None,
        help='Verbosity level (0 to 3) (default 1)')
    parser.add_argument(
        '--log', '-l', action='store_true', default=False,
        help='Enable file logging of all verbose text (default off)')
    parser.add_argument(
        '--logfile', '-g', type=str, default=None,
        help='Specify file for logging (default {})'.format(DEFAULT_LOGFILES[sensor-1]))
    parser.add_argument(
        '--datalogflag', '-d', action='store_true', default=False,
        help='Enable logging local data (default off)')
    parser.add_argument(
        '--datalog', '-f', default=None,
        help='Specify a path for the datalog (default {})'.format(DEFAULT_DATALOGS[sensor-1]))
    parser.add_argument(
        '--sender-mode', '-m', type=str, default=DEFAULT_SENDER_MODE,
        choices=['udp', 'tcp', 'UDP', 'TCP', 'udp_test', 'tcp_test'],
        help='The network protocol used in sending data ' +
        '(default {})'.format(DEFAULT_SENDER_MODE))
    parser.add_argument(
        '--aeskey', '-q', default=None,
        help='Specify the aes encription key, mainly used with the D3S ' +
        'because of the larger data packets (default {})'.format(DEFAULT_AESKEY))
    parser.add_argument(
        '--oled', '-o', action='store_true', default=False,
        help='Indicates whether an OLED screen is present or not')
    parser.add_argument(
        '--small_board', '-0', action='store_true', default=False,
        help='Indicates whether this is on a PiZero board or not')
    """
    parser.add_argument(
        '--oled_log', '-r', default=None,
        help='Specify a path for the datalog (default {})'.format(DEFAULT_OLED_LOGS[sensor-1]))
    """

    if sensor == 1:
        #Pocket Geiger specific variables.
        parser.add_argument(
            '--counts_LED_pin', '-z', default=None,
            help='Specify which pin the counts LED is connected to.')
        parser.add_argument(
            '--network_LED_pin', '-e', default=None,
            help='Specify which pin the network LED is connected to.')
        parser.add_argument(
            '--noise_pin', '-n', type=int, default=NOISE_PIN,
            help='Specify which pin to the noise reader is connected to ' +
            '(default {})'.format(NOISE_PIN))
        parser.add_argument(
            '--signal_pin', '-u', type=int, default=None,
            help='Specify which pin the signal is coming in from ' +
            '(default {})'.format(SIGNAL_PIN))

        args = parser.parse_args()
        arg_dict = vars(args)
        del arg_dict['sensor']

        mgr = Manager_Pocket(**arg_dict)

    if sensor == 2:
        #D3S specific variables.
        parser.add_argument(
            '--calibrationlog', '-j', default=None,
            help='Specify the calibration log for the D3S ' +
            '(default {})'.format(DEFAULT_CALIBRATIONLOG_D3S))
        parser.add_argument(
            '--calibrationlogflag', '-z', action='store_true', default=False,
            help='Specify whether the D3S should store a calibration log ' +
            '(default False)')
        parser.add_argument(
            '--calibrationlogtime', '-x', type=int, default=None,
            help='Specify the amount of time the D3S should take to calibrate ' +
            '(default 10 minutes)')
        parser.add_argument('--count', '-4', dest='count', default=0)
        parser.add_argument(
            '--d3s_LED_pin', '-3', default=None,
            help='Specify which pin the D3S LED is connected to.')
        parser.add_argument(
            '--d3s_LED_blink', '-b', default=True,
            help='Decides whether to blink the d3s LED when looking for the device ' +
            '(default On)')
        parser.add_argument(
            '--d3s_LED_blink_period_1', '-1', default=D3S_LED_BLINK_PERIOD_INITIAL,
            help='Specify the frequency that the D3S LED blinks ' +
            'when looking for the device (default {})'.format(D3S_LED_BLINK_PERIOD_INITIAL))
        parser.add_argument(
            '--d3s_LED_blink_period_2', '-2', default=D3S_LED_BLINK_PERIOD_DEVICE_FOUND,
            help='Specify the frequency that the D3S LED blinks when a device is ' +
            'found \nand is now waiting to recieve initial data from the device ' +
            '(default {})'.format(D3S_LED_BLINK_PERIOD_DEVICE_FOUND))
        parser.add_argument(
            '--d3s_light_switch', '-u', default=False,
            help='Specify whether the D3S LED should start on or not ' +
            '(default Off)')
        parser.add_argument('--device', '-e', dest='device', default='all')
        parser.add_argument(
            '--log-bytes', '-y', dest='log_bytes', default=False,
            action='store_true')
        parser.add_argument('--transport', '-n', default='usb')

        args = parser.parse_args()
        arg_dict = vars(args)
        del arg_dict['sensor']

        mgr = Manager_D3S(**arg_dict)

    if sensor == 3:
        #Air Quality Sensor specific variables.
        parser.add_argument(
            '--AQ_port', '-a', default=DEFAULT_AQ_PORT,
            help='Specify which port the Air Quality sensor is sending ' +
            'data through \n[note, this is a Serial Port so be sure to use ' +
            'Serial port notation] (default {})'.format(DEFAULT_AQ_PORT))

        args = parser.parse_args()
        arg_dict = vars(args)
        del arg_dict['sensor']

        mgr = Manager_AQ(**arg_dict)

    if sensor == 4:
        #CO2 Sensor specific variables.
        parser.add_argument(
            '--CO2_port', '-a', default=None,
            help='Specify which port the CO2 sensor is sending ' +
            'data through \n[Note this is an Adafruit MCP port so be sure ' +
            'to use that notation]')

        args = parser.parse_args()
        arg_dict = vars(args)
        del arg_dict['sensor']

        mgr = Manager_CO2(**arg_dict)

    if sensor == 5:
        #Weather Sensor specific variables.
        parser.add_argument(
            '--Weather_Port', '-a', default=None,
            help='Specify which port the Weather sensor is sending ' +
            'data through \n[Note this is an I2C port so be sure ' +
            'to use that notation]')

        args = parser.parse_args()
        arg_dict = vars(args)
        del arg_dict['sensor']

        mgr = Manager_Weather(**arg_dict)

    try:
        mgr.run()

    except:
        if mgr.logfile:
            # print exception info to logfile
            with open(mgr.logfile, 'a') as f:
                traceback.print_exc(15, f)
        # regardless, re-raise the error which will print to stderr
        raise
