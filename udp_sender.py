#!/home/pi/miniconda/bin/python
# -*- coding: utf-8 -*-
##########################
#  Run on Raspberry Pis  #
##########################

import socket
import datetime
from time import sleep
import cust_crypt as ccrypt
import csv
import argparse
import RPi.GPIO as GPIO
from dosimeter import Dosimeter
from multiprocessing import Process
from dosimeter import SIG_PIN, NS_PIN


class Sender:
    def parseArguments(self):
        """
        Parse command-line arguments to udp_sender.
        """

        parser = argparse.ArgumentParser()
        parser.add_argument(
            '--test', '-t', action='store_true',
            help=('\n\t Testing CSV file handling, you should probably use ' +
                  '--filename to specify a non-default CSV file. \n ' +
                  'Note: CSV - Comma Separated Variable text file'))
        parser.add_argument(
            '--filename', '-f', nargs='?', type=str,
            default='/home/pi/dosenet/config-files/test-onerow.csv',
            help=('\n\t Must link to a CSV file with ... \n' +
                  'Default is "config-files/test-onerow.csv" - no "'))
        parser.add_argument(
            '--led_counts', nargs='?', required=False, type=int, default=21,
            help='\n\t The BCM pin number of the + end of the count LED\n')
        parser.add_argument(
            '--led_power', nargs='?', required=False, type=int, default=26,
            help='\n\t The BCM pin number of the + end of the power LED\n')
        parser.add_argument(
            '--led_network', nargs='?', required=False, type=int, default=20,
            help=('\n\t The BCM pin number of the + end of the networking ' +
                  'LED - pings berkeley.edu\n'))
        # nargs='?' means 0-or-1 arguments
        parser.add_argument('--ip', nargs=1, required=False, type=str)
        parser.add_argument(
            '--public_key', type=str,
            default='/home/pi/dosenet-raspberrypi/id_rsa_lbl.pub')
        self.args = parser.parse_args()
        self.file_path = self.args.filename
        self.led_network = self.args.led_network
        self.led_power = self.args.led_power
        self.led_counts = self.args.led_counts
        self.LEDS = dict(led_network=self.led_network,
                         led_power=self.led_power,
                         led_counts=self.led_counts)
        self.public_key = self.args.public_key
        print 'PUBLIC KEY!'
        print '    ' + self.public_key
        if self.args.test:
            print 'LED pins (BCM): ', self.LEDS

    def getContents(self, file_path):
        """
        Return content of csv file as list of dicts
        """
        content = []  # list()
        with open(file_path, 'r') as csvfile:
            csvfile.seek(0)
            # read the CSV file into a dictionary
            dictReader = csv.DictReader(csvfile)
            for row in dictReader:
                content.append(row)
        # Return list of dicts
        return content

    def initialise(self):
        if self.args.test:
            print '~ Testing CSV handling\n\n'
            print '- '*64
            print 'Test file:\t', self.file_path
            self.file_contents = self.getContents(self.file_path)
            csv = self.file_contents
            print '- ' * 64
            print '\t', type(csv), csv
            print '- ' * 64
            print '\n1st line dictonary object:\t\t', csv[0]
            print 'stationID element:\t', csv[0]['stationID']
            print 'message_hash element:\t', csv[0]['message_hash']
            print 'lat element:\t\t', csv[0]['lat']
            print 'long element:\t\t', csv[0]['long']
        else:
            print '~ Normal run, loading CSV configuration file'
            try:
                self.file_contents = self.getContents(self.file_path)
            except Exception, e:
                print '\n\tIs this running on a Raspberry Pi?'
                print ('\tIf so, make sure the \'RPi\' package is installed ' +
                       'with conda and or pip\n')
                print ('~~~~~ ERROR: Getting the CSV file contents failed ' +
                       '~~~~~\n')
                raise e

    def getDatafromCSV(self):
        # Load from config files
        csv = self.file_contents
        self.stationID = csv[0]['stationID']
        self.msg_hash = csv[0]['message_hash']

    def initVariables(self):
        self.pe = ccrypt.public_d_encrypt(key_file_lst=[self.public_key])
        self.IP = 'dosenet.dhcp.lbl.gov'
        self.port = 5005
        if self.args.ip:
            # Send to custom IP if testing
            self.IP = self.args.ip[0]
            print '\n\t Using specified IP: "%s"' % self.IP
        if self.args.test:
            print 'UDP target IP @ port :', self.IP + ':' + str(self.port)
        # uses UDP protocol
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    def deactivatePins(self):
        GPIO.output(self.led_power, False)
        GPIO.output(self.led_network, False)
        GPIO.output(self.led_power, False)
        GPIO.cleanup()

    def getAndSendData(self, det, startTime, endTime):
        count, cpm, cpm_error = det.getCPM(startTime, endTime)
        print 'Count: ', count, ' - CPM: ', cpm, '+/-', cpm_error
        # Only run the next segment after the warm-up phase
        if len(det.counts) > 1 and not self.args.test:
            # don't send data in test mode
            self.sendData(cpm=cpm, cpm_error=cpm_error)

    def sendData(self, cpm, cpm_error, error_code=0):
        # Default 'working' state - error code 0
        c = ','
        now = datetime.datetime.now()   # only used in test block below
        package = (str(self.msg_hash) + c +
                   str(self.stationID) + c +
                   str(cpm) + c +
                   str(cpm_error) + c + str(error_code))
        packet = self.pe.encrypt_message(package)[0]
        if self.args.test:
            print '- '*64, '\nRaw message: ', u'%s' % package
            # Next line really screws up Raspberry Pi terminal... without str()
            print 'Encrypted message: ', str(packet), '\n', '- '*64
            print ('Encrypted UDP Packet sent @ ' + str(now) +
                   ' - ' + str(self.IP) + ':' +
                   str(self.port) + '\n')
        try:
            self.socket.sendto(packet, (self.IP, self.port))
        except Exception as e:
            print str(e)
            print ''
            pass

    def main(self):
        # Initialise dosimeter object from dosimeter.py
        det = Dosimeter(max_accumulation_time_sec=3600, **self.LEDS)
        det.activatePin(self.led_power)
        sleep_time = 300
        if self.args.test:
            sleep_time = 10  # seconds
        dt = datetime.timedelta(seconds=sleep_time)

        # now we are keeping track of our accumulation time intervals
        #   in this block, not in Dosimeter
        curStart = datetime.datetime.now()
        curEnd = curStart + dt
        timeCheckFactor = 4

        while True:
            # Run until error or KeyboardInterrupt (Ctrl + C)
            p = Process(target=det.ping, args=(self.led_network,))
            p.start()
            p.join()
            # p.join() will block main thread execution until ping succeeds,
            #   else blinks in parallel
            GPIO.remove_event_detect(SIG_PIN)
            GPIO.add_event_detect(
                SIG_PIN, GPIO.FALLING, callback=det.updateCount_basic,
                bouncetime=1)
            while datetime.datetime.now() < curEnd:
                # Wait until the accumulation time interval is up
                # If timeCheckFactor==1, then the intervals of the while True
                #   loop would slowly get out of sync with the start/end times,
                #   due to the additional processing time for commands before
                #   and after the sleep command.
                sleep(sleep_time / timeCheckFactor)
            self.getAndSendData(det, curStart, curEnd)  # time in sec
            curStart = curEnd + datetime.timedelta(seconds=0)   # copy
            curEnd = curEnd + dt

if __name__ == "__main__":
    sen = Sender()
    sen.parseArguments()
    sen.initialise()
    sen.getDatafromCSV()
    sen.initVariables()
    try:
        sen.main()
    except (KeyboardInterrupt, SystemExit):
        print '.... User interrupt ....\n Byyeeeeeeee'
    except Exception as e:
        print str(e)
    finally:
        print '~~ Deactivating pins and cleaning up. ~~'
        sen.deactivatePins()
