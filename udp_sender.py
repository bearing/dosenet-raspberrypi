#!/home/pi/miniconda/bin/python
# -*- coding: utf-8 -*-
##########################
## Run on Raspberry Pis ##
##########################
import numpy as np
import socket
import datetime
import time
from time import sleep
import cust_crypt as ccrypt
import os
import csv
import sys
import argparse
import RPi.GPIO as GPIO
from dosimeter import Dosimeter
import subprocess
from multiprocessing import Process
import email_message

class Sender:
    def parseArguments(self):
        parser = argparse.ArgumentParser()
        parser.add_argument('--test', '-t',action='store_true',
            help='\n\t Testing CSV file handling, you should probably use --filename to specify a \
                non-default CSV file. \n Note: CSV - Comma Separated Variable text file')
        parser.add_argument('--filename','-f',nargs='?',type=str,default='/home/pi/dosenet/config-files/test-onerow.csv',
            help='\n\t Must link to a CSV file with  \n \
                Default is \"config-files/test-onerow.csv\" - no \"')
        parser.add_argument('--led_counts',nargs='?',required=False,type=int, default=21,
            help='\n\t The BCM pin number of the + end of the count LED\n')
        parser.add_argument('--led_power',nargs='?',required=False,type=int, default=26,
            help='\n\t The BCM pin number of the + end of the power LED\n')
        parser.add_argument('--led_network',nargs='?',required=False,type=int, default=20,
            help='\n\t The BCM pin number of the + end of the networking LED - pings berkeley.edu\n')
                                       # nargs='?' means 0-or-1 arguments
        parser.add_argument('--ip',nargs=1,required=False,type=str)
        self.args = parser.parse_args()
        self.file_path = self.args.filename
        self.led_network = self.args.led_network
        self.led_power = self.args.led_power
        self.led_counts = self.args.led_counts
        self.LEDS = dict(led_network = self.led_network,
                        led_power = self.led_power,
                        led_counts = self.led_counts)
        if self.args.test:
            print 'LED pins (BCM): ', self.LEDS

    def getContents(self,file_path):
        content = [] #list()
        with open(file_path, 'r') as csvfile:
            csvfile.seek(0)
            dictReader = csv.DictReader(csvfile) #read the CSV file into a dictionary
            for row in dictReader:
                content.append(row)
        return content # List of dicts

    def initialise(self):
        if self.args.test:
            print '~ Testing CSV handling\n\n'
            print '- '*64
            print 'Test file:\t',self.file_path
            self.file_contents = self.getContents(self.file_path)
            csv = self.file_contents
            print '- '*64
            print '\t',type(csv), csv
            print '- '*64
            print '\n1st line dictonary object:\t\t', csv[0]
            print 'stationID element:\t', csv[0]['stationID']
            print 'message_hash element:\t', csv[0]['message_hash']
            print 'lat element:\t\t',  csv[0]['lat']
            print 'long element:\t\t', csv[0]['long']
        else:
            print '~ Normal run, loading CSV configuration file'
            try:
                self.file_contents = self.getContents(self.file_path)
            except Exception, e:
                print '\n\tIs this running on a Raspberry Pi?'
                print '\tIf so, make sure the \'RPi\' package is installed with conda and or pip\n'
                print '~~~~~ ERROR: Getting the CSV file contents failed ~~~~~\n'
                raise e
                sys.exit(0)

    def getDatafromCSV(self): # Load from config files
        csv = self.file_contents
        self.stationID = csv[0]['stationID']
        self.msg_hash =  csv[0]['message_hash']

    def initVariables(self):
        public_key = ['/home/pi/dosenet/ssh_keys/id_rsa_lbl.pub']
        self.pe = ccrypt.public_d_encrypt(key_file_lst = public_key)
        self.IP = 'dosenet.dhcp.lbl.gov'
        self.port = 5005
        if self.args.ip:
            self.IP = self.args.ip[0] #Send to custom IP if testing
            print '\n\t Using specified IP: "%s"' % self.IP
        if self.args.test:
            print 'UDP target IP @ port :', self.IP + ':' + str(self.port)
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # uses UDP protocol

    def deactivatePins(self):
        GPIO.output(self.led_power,False)
        GPIO.output(self.led_network,False)
        GPIO.output(self.led_power,False)
        GPIO.cleanup()

    def getAndSendData(self, det, sleep_time = 300):
        cpm, cpm_error = det.getCPM(accumulation_time = sleep_time)
        count = det.getCount()
        print 'Count: ', count,' - CPM: ', cpm, '+/-', cpm_error
        if len(det.counts) > 1: # Only run the next segment after the warm-up phase
            self.sendData(cpm = cpm, cpm_error = cpm_error)

    def sendData(self, cpm, cpm_error, error_code = 0):
        # Default 'working' state - error code 0
        c = ','
        now = datetime.datetime.now()
        package = str(self.msg_hash) +c+ str(self.stationID) +c+ str(cpm) +c+ \
                  str(cpm_error) +c+ str(error_code)
        packet = self.pe.encrypt_message(package)[0]
        if self.args.test:
            print '- '*64, '\nRaw message: ', u'%s' % package
            print 'Encrypted message: ', str(packet), '\n', '- '*64 # This really screws up Raspberry Pi terminal... without str()
            print 'Encrypted UDP Packet sent @ '+ str(now )+ ' - ' + \
                    str(self.IP)+':'+str(self.port),'\n'
        try:
            self.socket.sendto(packet, (self.IP, self.port))
        except Excpetion as e:
            print str(e)
            print ''
            pass

    def main(self):
        det = Dosimeter(**self.LEDS)  # Initialise dosimeter object from dosimeter.py
        det.activatePin(self.led_power)
        sleep_time = 300
        if self.args.test:
            sleep_time = 10 # seconds
        while True: # Run until error or KeyboardInterrupt (Ctrl + C)
            p = Process(target = det.ping, args=(self.led_network,))
            p.start()
            p.join() # Will block main thread execution until ping succeeds, else blinks in parallel
            GPIO.remove_event_detect(24)
            GPIO.add_event_detect(24, GPIO.FALLING, callback = det.updateCount_basic, bouncetime=1)
            sleep(sleep_time)
            self.getAndSendData(det = det, sleep_time = sleep_time) # time in seconds

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
