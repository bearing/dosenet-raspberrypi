# globalvalues.py: provide constants all in one place.

# -*- coding: utf-8 -*-
from __future__ import print_function
import serial
try:
    import Adafruit_MCP3008
except:
    pass
try:
    from Adafruit_BME280 import *
except:
    pass
import os

try:
    import RPi.GPIO as GPIO
    RPI = True
except ImportError:
    print('Not on a Raspberry Pi, proceeding anyway')
    RPI = False

# Hardware pin numbers
# (using Broadcom numbering)
# (Broadcom numbers are labeled on the pi hat)
SIGNAL_PIN = 17
NOISE_PIN = 4
NEW_D3S_LED_PIN = 13
NEW_NETWORK_LED_PIN = 16
NEW_COUNTS_LED_PIN = 19
OLD_COUNTS_LED_PIN = 21
OLD_NETWORK_LED_PIN = 20
OLD_D3S_LED_PIN = 19

NETWORK_LED_BLINK_PERIOD_S = 1.5
NETWORK_LED_BLINK_LOST_CONNECTION = 0.75

# Defaults
DEFAULT_CONFIG = '/home/pi/config/config.csv'
DEFAULT_PUBLICKEY = '/home/pi/config/id_rsa_lbl.pub'
DEFAULT_AESKEY = '/home/pi/config/secret.aes'
DEFAULT_LOGFILE = '/home/pi/debug.log'
DEFAULT_LOGFILE_D3S = '/home/pi/debug.log_D3S'
DEFAULT_LOGFILE_AQ = '/home/pi/debug.log_AQ'
DEFAULT_LOGFILE_CO2 = '/home/pi/debug.log_CO2'
DEFAULT_LOGFILE_WEATHER = '/home/pi/debug.log_weather'
DEFAULT_HOSTNAME = 'dosenet.dhcp.lbl.gov'
DEFAULT_UDP_PORT = 5005
TESTING_UDP_PORT = 5006
DEFAULT_TCP_PORT = 5100
TESTING_TCP_PORT = 5101
BOOT_LOG_CODE = 11
DEFAULT_SENDER_MODE = 'tcp'
DEFAULT_DATALOG = '/home/pi/data-log.txt'
DEFAULT_DATALOG_D3S = '/home/pi/data-log_D3S.txt'
DEFAULT_DATALOG_AQ = '/home/pi/data-log_AQ.txt'
DEFAULT_DATALOG_CO2 = '/home/pi/data-log_CO2.txt'
DEFAULT_DATALOG_WEATHER = '/home/pi/data-log_weather.txt'
DEFAULT_DATA_BACKLOG_FILE = '/home/pi/data_backlog_file.txt'
DEFAULT_DATA_BACKLOG_FILE_D3S = '/home/pi/data_backlog_file_D3S.csv'
DEFAULT_DATA_BACKLOG_FILE_AQ = '/home/pi/data_backlog_file_AQ.txt'
DEFAULT_DATA_BACKLOG_FILE_CO2 = '/home/pi/data_backlog_file_CO2.txt'
DEFAULT_DATA_BACKLOG_FILE_WEATHER = '/home/pi/data_backlog_file_weather.txt'
DEFAULT_CALIBRATIONLOG_D3S = '/home/pi/calibration-log_D3S.txt'
DEFAULT_CALIBRATIONLOG_TIME = 600
DEFAULT_PROTOCOL = 'new'

DEFAULT_INTERVAL_NORMAL = 300
DEFAULT_INTERVAL_TEST = 30
DEFAULT_MAX_ACCUM_TIME = 3600
FLUSH_PAUSE_S = 2

DEFAULT_INTERVAL_NORMAL_D3S = 300
DEFAULT_INTERVAL_TEST_D3S = 30
DEFAULT_D3STEST_TIME = 5
D3S_LED_BLINK_PERIOD_INITIAL = 0.75
D3S_LED_BLINK_PERIOD_DEVICE_FOUND = 0.325

try:
    DEFAULT_AQ_PORT = serial.Serial("/dev/serial0", baudrate=9600, timeout=1.5)
except:
    print("No AQ Sensor setup, proceeding without initializing AQ Port.")
DEFAULT_INTERVAL_NORMAL_AQ = 300
DEFAULT_INTERVAL_TEST_AQ = 30
AQ_VARIABLES = ['PM 1.0', 'PM 2.5', 'PM 10 ', '0.3 um', '0.5 um',
            '1.0 um', '2.5 um', '5.0 um', '10 um ']

CLK, MISO, MOSI, CS = 18, 23, 24, 25
try:
    DEFAULT_CO2_PORT = Adafruit_MCP3008.MCP3008(clk=CLK, cs=CS, miso=MISO, mosi=MOSI)
except:
    print("No CO2 Sensor setup, proceeding without initializing Weather Port.")
DEFAULT_INTERVAL_NORMAL_CO2 = 300
DEFAULT_INTERVAL_TEST_CO2 = 30
CO2_VARIABLES = ['CO2 Concentration in ppm', 'UV index']

try:
    DEFAULT_WEATHER_PORT = BME280(t_mode=BME280_OSAMPLE_8, p_mode=BME280_OSAMPLE_8, h_mode=BME280_OSAMPLE_8)
except:
    print("No Weather Sensor setup, proceeding without initializing Weather Port.")
DEFAULT_INTERVAL_NORMAL_WEATHER = 300
DEFAULT_INTERVAL_TEST_WEATHER = 30
WEATHER_VARIABLES = ['temperature', 'pressure', 'humidity']
WEATHER_VARIABLES_UNITS = ['deg C', 'hPa', '%']

try:
    DEFAULT_AQ_PORT = serial.Serial("/dev/serial0", baudrate=9600, timeout=1.5)
except:
    print("No AQ Sensor detected, proceeding without initializing AQ Port.")
DEFAULT_INTERVAL_NORMAL_AQ = 300
DEFAULT_INTERVAL_TEST_AQ = 30
AQ_VARIABLES = ['PM 1.0', 'PM 2.5', 'PM 10', '0.3 um', '0.5 um',
            '1.0 um', '2.5 um', '5.0 um', '10 um']
# ANSI color codes
ANSI_RESET = '\033[0m'
ANSI_BOLD = '\033[1m'
ANSI_RED = '\033[31m' + ANSI_BOLD
ANSI_GR = '\033[32m' + ANSI_BOLD
ANSI_YEL = '\033[33m' + ANSI_BOLD
ANSI_BLUE = '\033[34m' + ANSI_BOLD
ANSI_CYAN = '\033[36m' + ANSI_BOLD

REBOOT_SCRIPT = '/home/pi/dosenet-raspberrypi/git-pull-reboot.sh'
GIT_DIRECTORY = '/home/pi/dosenet-raspberrypi/'

"""
Command line output statements used in the data-handlers
"""

SENSOR_NAMES = ['Pocket Geiger Counter', 'D3S', 'Air Quality Sensor',
    'CO2 Sensor', 'Weather Sensor']

DATA_NAMES = ['pocket geiger data', 'D3S data', 'air quality data', 'CO2 data', 'weather/temp/humidity data']

NEW_SENSOR_DISPLAY_TEXT = (
    '{green}Starting the {{sensor_name}} with new LED pins.{reset}').format(
    green=ANSI_GR, reset=ANSI_RESET)

OLD_SENSOR_DISPLAY_TEXT = (
    '{green}Starting the {{sensor_name}} with old LED pins.{reset}').format(
    green=ANSI_GR, reset=ANSI_RESET)

RUNNING_DISPLAY_TEXT = (
    '{green}Manager is starting to run at {{start_time}}' +
    ' on {{date}}' + '\nand is running with intervals ' +
    'of {{interval}} seconds.{reset}').format(
    green=ANSI_GR, reset=ANSI_RESET)

CPM_DISPLAY_TEXT = (
    '{green} {{counts}}{reset}' + '{cyan} total counts with {reset}' +
    '{green}{{cpm:.2f}}{reset}' + '{cyan} counts per minute\n{reset}' +
    '{cyan} and an error on the cpm of: {reset}' + '{green}+/- {{cpm_err:.2f}}{reset}').format(
    green=ANSI_GR, cyan=ANSI_CYAN, reset=ANSI_RESET)

SPECTRA_DISPLAY_TEXT = (
    '{cyan} Total counts gathered: {reset}' + '{green}{{total_counts}}{reset}').format(
    green=ANSI_GR, reset=ANSI_RESET, cyan=ANSI_CYAN)

AQ_PM_DISPLAY_TEXT = (
	'{cyan} {{variable}} ={reset}' +
	'{green} {{avg_data:0.2f}} {reset}' +
    '{cyan}ug/m3 {reset}').format(
    cyan=ANSI_CYAN, reset=ANSI_RESET, green=ANSI_GR)

AQ_P_DISPLAY_TEXT = (
	'{cyan} # of Particles over {{variable}} ={reset}' +
	'{green} {{avg_data:0.2f}} {reset}').format(
    cyan=ANSI_CYAN, reset=ANSI_RESET, green=ANSI_GR)

CO2_DISPLAY_TEXT = (
    '{cyan} The average {{variable}}{reset}' +
    '{cyan} was: {reset}' + '{green}{{data:0.2f}}{reset}').format(
    cyan=ANSI_CYAN, reset=ANSI_RESET, yellow=ANSI_YEL, green=ANSI_GR)

WEATHER_DISPLAY_TEXT = (
    '{cyan} The average {{variable}} was: {reset}' +
    '{green}{{data:0.2f}} {{unit}}{reset}').format(cyan=ANSI_CYAN,
    green=ANSI_GR, reset=ANSI_RESET)

TIME_DISPLAY_TEXT = (
    '{red} This data was gathered from: {reset}' +
    '{yellow}{{start_time}}{reset}' + '{red} to {reset}' +
    '{yellow}{{end_time}}{reset}' + '{red} on {reset}'+
    '{yellow}{{date}}{reset}').format(
    red=ANSI_RED, reset=ANSI_RESET, yellow=ANSI_YEL)

SINGLE_BREAK_LINE = (
    '\n{blue}-----------------------------------------------------------\n{reset}').format(
    blue=ANSI_BLUE, reset=ANSI_RESET)

DOUBLE_BREAK_LINE = (
    '\n{blue}-----------------------------------------------------------\n{reset}' +
    '\n{blue}-----------------------------------------------------------\n{reset}').format(
    blue=ANSI_BLUE, reset=ANSI_RESET)

strf = '%H:%M:%S'

# --- some old notes:
# Note: GPIO.LOW  - 0V
#       GPIO.HIGH - 3.3V or 5V ???? (RPi rail voltage)

# SIG >> float (~3.3V) --> 0.69V --> EXP charge back to float (~3.3V)
# NS  >> ~0V (GPIO.LOW) --> 3.3V (GPIO.HIGH) RPi rail
