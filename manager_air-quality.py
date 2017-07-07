import time
import argparse
import signal
import sys

from globalvalues import RPI
if RPI:
    import RPi.GPIO as GPIO

class Manager_Air_Quality(object):

    def __init__(self):
        
