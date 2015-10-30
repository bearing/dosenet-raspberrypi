#!/home/pi/miniconda/bin/python
# -*- coding: utf-8 -*-
#
# Ryan Pavlovsky (until Mon Jun 15 2015)
# Navrit Bal (after Jun 15 2015)
# DoseNet
# Applied Nuclear Physics Division
# Lawrence Berkeley National Laboratory, Berkeley, U.S.A.
# Adapted from dosimeter.py (Ryan Pavlovsky)
# Last updated: Mon 03/08/15
#################################
# Indirectly run on Raspberry Pis
#################################

import RPi.GPIO as GPIO
import numpy as np
import datetime
from time import sleep
import os
import email_message
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


class Dosimeter:
    """
    Dosimeter object connects to RPi GPIO and responds to interrupts to record
    counts. It provides getCPM method but does not handle the accumulation
    times.
    """

    def __init__(self, led_network=20, led_power=26, led_counts=21,
                 max_accumulation_time_sec=3600):
        """
        RPi hardware setup: LEDs, signals
        """

        self.LEDS = dict(led_network=led_network,
                         led_power=led_power,
                         led_counts=led_counts)
        self.counts = collections.deque([])  # Datetime queue

        # [BCP] now accumulation time is handled outside of Dosimeter.
        #       Dosimeter just keeps all counts within the last
        #       maxAccumulationTime
        self.maxAccumulationTime = datetime.timedelta(
            seconds=max_accumulation_time_sec)

        # Use Broadcom GPIO numbers - GPIO numbering system
        # eg. GPIO NS_PIN > pin 16. Not BOARD numbers, eg. 1, 2 ,3 etc.
        GPIO.setmode(GPIO.BCM)
        # SIG Sets up radiation detection; Uses pull up resistor on RPi
        GPIO.setup(SIG_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.add_event_detect(
            SIG_PIN, GPIO.FALLING,
            callback=self.updateCount_basic,
            bouncetime=1)
        GPIO.setup(led_network, GPIO.OUT)
        GPIO.setup(led_power, GPIO.OUT)
        GPIO.setup(led_counts, GPIO.OUT)

    def updateCount_basic(self, channel=SIG_PIN):
        """
        Run this as the callback from the detector signal interrupt.
        Add one count to the list.
        """

        now = datetime.datetime.now()
        # TODO: put datetimes in one queue,
        #  and let the main (non-interrupt) thread handle converting them
        #  in a 'flush' operation.
        timeFloat = (now - EPOCH_START_TIME).total_seconds()
        # Update datetime List
        self.counts.append(timeFloat)
        print '~~~  COUNT:', now
        # Blink count LED (#20)
        self.blink(pin=self.LEDS['led_counts'], timeInterval=0.01)

    def resetCounts(self, refTime):
        """
        Remove any counts in the queue that are older than maxAccumulationTime.
        """
        # refTime should be "now"
        # counts before (refTime - maxAccumulationTime) get removed

        if len(self.counts) == 0:
            # nothing to do, and "while self.counts[0]" will error
            return
        while self.counts[0] < (refTime - self.maxAccumulationTime):
            self.counts.popleft()

    def getCPM(self, startTime, endTime):
        """
        Calculate the CPM for the time interval between startTime and endTime.

        If startTime is farther back in time than maxAccumulationTime, this
        will not be accurate because those counts are already forgotten.
        """

        startTimeFloat = (startTime - EPOCH_START_TIME).total_seconds()
        endTimeFloat = (endTime - EPOCH_START_TIME).total_seconds()

        # convert to np.ndarray in order to perform elementwise logic
        countsArray = np.array(self.counts)
        count = np.sum(np.logical_and(
            countsArray > startTimeFloat, countsArray < endTimeFloat))
        count_err = np.sqrt(count)
        countingTime_sec = endTimeFloat - startTimeFloat  # already in seconds
        if countingTime_sec > 0:
            cpm = count / countingTime_sec * 60
            cpm_err = count_err / countingTime_sec * 60
        else:
            cpm, cpm_err = 0, 0

        return count, cpm, cpm_err

    def ping(self, pin=20, hostname='dosenet.dhcp.lbl.gov'):
        """
        Check whether DoseNet server is up.
        """

        response = os.system('ping -c 1 ' + str(hostname) + '> /dev/null')
        # and then check the response...
        if response == 0:
            print '~ ', hostname, 'is up!'
            self.activatePin(pin=pin)
            return True
        else:
            print '~ ', hostname, 'is DOWN!'
            self.blink(pin=pin, timeInterval=2, number_of_flashes=5)
            self.ping()

    def activatePin(self, pin):
        """Set pin output to True/HIGH"""
        GPIO.output(pin, True)
        # print 'Pin ON #:',pin,' - ',datetime.datetime.now()

    def deactivatePin(self, pin):
        """Set pin output to False/LOW"""
        GPIO.output(pin, False)
        # print 'Pin OFF #:',pin,' - ',datetime.datetime.now()

    def invertPin(self, pin):
        """Invert pin output"""
        GPIO.output(pin, not GPIO.input(pin))

    def blink(self, pin=21, timeInterval=1, number_of_flashes=1):
        """Flash LED at pin on timeInterval, number_of_flashes times"""
        for i in range(0, number_of_flashes):
            # Flash
            print '\t\t * #%s' % pin
            self.deactivatePin(pin)
            sleep(0.005)
            self.activatePin(pin)
            sleep(timeInterval / 2)
            self.deactivatePin(pin)
            sleep(timeInterval / 2)

    def __del__(self):
        print ('Dosimeter object just died - __del__')
        self.close()

    def __exit__(self):
        print ('Dosimeter object just exited - __exit__')
        self.close()

    def close(self):
        print('Actually closing now')
        GPIO.cleanup()

if __name__ == "__main__":
    """
    Test code is currently broken!
    """
    # TODO: rewrite this test code for Brian's changes

    det = Dosimeter()
    response = det.ping()
    print 'Ping DoseNet server test: ', response
    data = det.getCPM()
    print data
    det.updateCount_basic()
    print det.counts
    det.counts = []
    print '~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~'
    print '~~~~ Basic testing done. Entering while True loop ~~~~'
    print ' Waiting for Ctrl + C'
    MEASURE_TIME = 10
    count = 0
    while True:
        try:
            GPIO.remove_event_detect(SIG_PIN)
            GPIO.add_event_detect(SIG_PIN, GPIO.FALLING,
                                  callback=det.updateCount_basic, bouncetime=1)
            sleep(1)
            cpm, cpm_err = det.getCPM(accumulation_time=MEASURE_TIME)
            print '\t', 'CPM: ', cpm, u'±', cpm_err, '\n'
        except (KeyboardInterrupt, SystemExit):
            print '.... User interrupt ....\n Byyeeeeeeee'
        except Exception as e:
            print str(e)
            print 'Sending email'
            email_message.send_email(process=os.path.basename(__file__),
                                     error_message=str(e))
        finally:
            GPIO.cleanup()
