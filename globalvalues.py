# globalvalues.py: provide constants all in one place.

# -*- coding: utf-8 -*-
from __future__ import print_function

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
POWER_LED_PIN = 19
NETWORK_LED_PIN = 20
COUNTS_LED_PIN = 21

NETWORK_LED_BLINK_PERIOD_S = 1.5

# Defaults
DEFAULT_CONFIG = '/home/pi/config/config.csv'
DEFAULT_PUBLICKEY = '/home/pi/config/id_rsa_lbl.pub'
DEFAULT_AESKEY = '/home/pi/config/secret.aes'
DEFAULT_LOGFILE = '/home/pi/debug.log'
DEFAULT_LOGFILE_D3S = '/home/pi/debug.log_D3S.txt'
DEFAULT_HOSTNAME = 'dosenet.dhcp.lbl.gov'
DEFAULT_UDP_PORT = 5005
TESTING_UDP_PORT = 5006
DEFAULT_TCP_PORT = 5100
TESTING_TCP_PORT = 5101
DEFAULT_SENDER_MODE = 'tcp'
DEFAULT_DATALOG = '/home/pi/data-log.txt'
DEFAULT_DATALOG_D3S = '/home/pi/data-log_D3S.txt'
DEFAULT_DATA_BACKLOG_FILE = '/home/pi/data_backlog_file.txt'
DEFAULT_DATA_BACKLOG_FILE_D3S = '/home/pi/data_backlog_file_D3S.csv'
DEFAULT_CALIBRATIONLOG_D3S = '/home/pi/calibration-log_D3S.txt'
DEFAULT_CALIBRATIONLOG_TIME = 600
DEFAULT_PROTOCOL = 'new'

DEFAULT_INTERVAL_NORMAL = 300
DEFAULT_INTERVAL_TEST = 30
DEFAULT_MAX_ACCUM_TIME = 3600

DEFAULT_INTERVAL_NORMAL_D3S = 60
DEFAULT_INTERVAL_TEST_D3S = 10

# ANSI color codes
ANSI_RESET = '\033[0m'
ANSI_BOLD = '\033[1m'
ANSI_RED = '\033[31m' + ANSI_BOLD
ANSI_GR = '\033[32m' + ANSI_BOLD
ANSI_YEL = '\033[33m' + ANSI_BOLD

REBOOT_SCRIPT = '/home/pi/dosenet-raspberrypi/git-pull-reboot.sh'
GIT_DIRECTORY = '/home/pi/dosenet-raspberrypi/'

# --- some old notes:
# Note: GPIO.LOW  - 0V
#       GPIO.HIGH - 3.3V or 5V ???? (RPi rail voltage)

# SIG >> float (~3.3V) --> 0.69V --> EXP charge back to float (~3.3V)
# NS  >> ~0V (GPIO.LOW) --> 3.3V (GPIO.HIGH) RPi rail
