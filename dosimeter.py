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

SIG_PIN = 17
NS_PIN = 4

# SIG >> float (~3.3V) --> 0.69V --> EXP charge back to float (~3.3V)
# NS  >> ~0V (GPIO.LOW) --> 3.3V (GPIO.HIGH) RPi rail

# Note: GPIO.LOW  - 0V
#       GPIO.HIGH - 3.3V or 5V ???? (RPi rail voltage)


class Dosimeter:
    def __init__(self, led_network=20, led_power=26, led_counts=21):
        self.LEDS = dict(led_network=led_network,
                         led_power=led_power,
                         led_counts=led_counts)
        self.counts = []  # Datetime list
        # self.noise  = [] # Datetime list
        start = datetime.datetime.now()
        # Initialise with the starting time so getCPM doesn't get IndexError -
        #   needs a 1 item minimum for [0] to work
        self.counts.append(start)

        # self.noise.append(start)
        # # Initialise with the starting time so updateCount doesn't get
        # #   IndexError - needs a 1 item minimum for [-1] to work
        # self.microphonics = [] # errorFlag list
        # self.margin = datetime.timedelta(microseconds = 100000) # 100ms
        # # milliseconds is not an option

        # Use Broadcom GPIO numbers - GPIO numbering system
        # eg. GPIO NS_PIN > pin 16. Not BOARD numbers, eg. 1, 2 ,3 etc.
        GPIO.setmode(GPIO.BCM)
        # SIG Sets up radiation detection; Uses pull up resistor on RPi
        GPIO.setup(SIG_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        # NS Sets up microphonics detection; Uses pull up resistor on RPi
        # GPIO.setup(NS_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.add_event_detect(
            SIG_PIN, GPIO.FALLING,
            callback=self.updateCount_basic,
            bouncetime=1)
        # GPIO.add_event_detect(
        #     NS_PIN, GPIO.FALLING, callback=self.updateNoise, bouncetime=1000)
        GPIO.setup(led_network, GPIO.OUT)
        GPIO.setup(led_power, GPIO.OUT)
        GPIO.setup(led_counts, GPIO.OUT)

    def updateCount_basic(self, channel=SIG_PIN):
        now = datetime.datetime.now()
        # Update datetime List
        self.counts.append(now)
        print '~~~  COUNT:', now
        # Blink count LED (#20)
        self.blink(pin=self.LEDS['led_counts'], frequency=0.01)

    """def updateNoise(self,channel=NS_PIN):
        if not self.first_noise:
            #Avoids IndexError from the initialisation issue
            #print 'updateNoise - ', str(datetime.datetime.now())
            self.noise.append(datetime.datetime.now())
            print '\t\t\t\t NOISE only'
        else:
            self.first_noise = False
            print '\t~~ Haven\'t got any noise yet ~~'"""

    """def updateCount(self,channel=SIG_PIN):
        GPIO.setmode(GPIO.BCM)
        #noiseInput = GPIO.input(NS_PIN)
        now = datetime.datetime.now()
        if noiseInput: # == 1/True
            self.noise.append(now)
            print '\t\t\t\t NOISE only'
        elif not noiseInput: # ==0/False
            lastNoise = self.noise[-1] # Last datetime object in the noise list
            # Checks to see if microphonics detected within a 200ms window
            #   before deciding whether to change the
            # errorFlag to 'microphonics was HIGH' or leave as default
            if not (now - self.margin) <= lastNoise <= (now + self.margin):
                print '. #', int(self.getCount())
                self.counts.append(now) # Stores counts as a list of datetimes
                self.blink()
                # errorFlag = False by default (no error registered)
                self.microphonics.append(False)
                # Remove later
                cpm, err = self.getCPM(); print cpm
            else:
                self.counts.append(now) # Stores counts as a list of datetimes
                self.blink()
                self.microphonics.append(True)
                print 'counts + ** NOISE **'
                # Remove later
                cpm, err = self.getCPM(); print cpm
                # print 'Stop shaking meeeeee'
        else:
            print '\n\t\t\t NS was not GPIO.HIGH or GPIO.LOW'"""

    def countsToArr(self):
        self.counts = np.array(self.counts, dtype='M8[us]')

    def countsToList(self):
        self.counts = self.counts.tolist()

    def resetCounts(self, seconds=300):
        try:
            self.countsToArr()
        except Exception as e:
            print '~~ Error: could not convert to array. ~~'
            print str(e)
        try:
            """Saves only the last number of seconds of events
            Moving window
            Will lead to exponential decay behaviour...
            Change to fixed window scheme?"""
            # print 'Last count: ', self.counts[-1]
            # print 'All counts: ', self.counts
            # Courtesy of Joey
            self.counts = self.counts[self.counts > self.counts[-1] -
                                      np.timedelta64(seconds, 's')]
        except Exception as e:
            print '~~ Error: Could not clip counts. ~~'
            print str(e)
        try:
            self.countsToList()
        except Exception as e:
            print '~~ Error: Could not convert to list. ~~'
            print str(e)

    def getCount(self):
        return float(len(self.counts))

    def getCPM(self, accumulation_time=300):
        now = datetime.datetime.now()
        count = self.getCount()
        if count < 2:
            return 0, 0
        count_err = np.sqrt(count)
        counting_time = (now - self.counts[0]).total_seconds()
        cpm = count / counting_time * 60
        cpm_err = count_err / counting_time * 60
        # Default last 5 minutes of counts
        if(counting_time > accumulation_time):
            print '\n\t\t ~~~~ RESET ~~~~\n'
            self.resetCounts(seconds=accumulation_time)
        return cpm, cpm_err

    def ping(self, pin=20, hostname='dosenet.dhcp.lbl.gov'):
        response = os.system('ping -c 1 ' + str(hostname) + '> /dev/null')
        # and then check the response...
        if response == 0:
            print '~ ', hostname, 'is up!'
            self.activatePin(pin=pin)
            return True
        else:
            print '~ ', hostname, 'is DOWN!'
            self.blink(pin=pin, frequency=2, number_of_flashes=5)
            self.ping()

    def activatePin(self, pin):
        GPIO.output(pin, True)
        # print 'Pin ON #:',pin,' - ',datetime.datetime.now()

    def deactivatePin(self, pin):
        GPIO.output(pin, False)
        # print 'Pin OFF #:',pin,' - ',datetime.datetime.now()

    def invertPin(self, pin):
        GPIO.output(pin, not GPIO.input(pin))

    def blink(self, pin=21, frequency=1, number_of_flashes=1):
        for i in range(0, number_of_flashes):
            # Flash
            print '\t\t * #%s' % pin
            self.deactivatePin(pin)
            sleep(0.005)
            self.activatePin(pin)
            sleep(frequency / 2)
            self.deactivatePin(pin)
            sleep(frequency / 2)

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
