#!/usr/bin/env python
import os
import multiprocessing
import serial
import signal
import argparse

def start_dosenet(mode):
    if mode == 0:
        os.system('sudo bash /home/pi/dosenet-raspberrypi/pocket.sh start')
    if mode == 1:
        os.system('sudo bash /home/pi/dosenet-raspberrypi/pocket.sh test')

def start_D3S(mode):
    if mode == 0:
        os.system('sudo bash /home/pi/dosenet-raspberrypi/D3S.sh start')
    if mode == 1:
        os.system('sudo bash /home/pi/dosenet-raspberrypi/D3S.sh test')

def start_AQ(mode):
    if mode == 0:
        os.system('sudo bash /home/pi/dosenet-raspberrypi/AQ.sh start')
    if mode == 1:
        os.system('sudo bash /home/pi/dosenet-raspberrypi/AQ.sh test')

def start_CO2(mode):
    if mode == 0:
        os.system('sudo bash /home/pi/dosenet-raspberrypi/CO2.sh start')
    if mode == 1:
        os.system('sudo bash /home/pi/dosenet-raspberrypi/CO2.sh test')

def start_Weather(mode):
    if mode == 0:
        os.system('sudo bash /home/pi/dosenet-raspberrypi/weather.sh start')
    if mode == 1:
        os.system('sudo bash /home/pi/dosenet-raspberrypi/weather.sh test')

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--test_mode', action='store_true', default=False,
        help="Choose whether the devices will start in test mode or not. (Default False)")
    test_mode = parser.parse_args().test_mode

    if not test_mode:
        print('Waiting for NTP to be synced...')
        os.system('sudo service ntp stop')
        os.system('sudo timeout 60s ntpd -gq')
        os.system('sudo service ntp start')

    try:
        ser = serial.Serial('/dev/ttyACM0')
        ser.flushInput()
        ser.close()
    except:
        pass

    if test_mode:
        a = multiprocessing.Process(target=start_AQ, args=(1,))
        c = multiprocessing.Process(target=start_CO2, args=(1,))
        w = multiprocessing.Process(target=start_Weather, args=(1,))
    else:
        p = multiprocessing.Process(target=start_D3S, args=(0,))
        t = multiprocessing.Process(target=start_dosenet, args=(0,))
        a = multiprocessing.Process(target=start_AQ, args=(0,))
        c = multiprocessing.Process(target=start_CO2, args=(0,))
        w = multiprocessing.Process(target=start_Weather, args=(0,))

    try:
        """
        print('Starting D3S script process')
        p.start()
        print('Starting Pocket Geiger script process')
        t.start()
        """
        print('Starting Air Quality Sensor script process')
        a.start()
        print('Starting CO2 sensor script process')
        c.start()
        print('Starting Weather sensor script process')
        w.start()
        print('started')
        #p.join()
        #t.join()
        a.join()
        c.join()
        w.join()
        print('we can reboot here')
    except:
        pass
