#!/usr/bin/env python
import os
import multiprocessing
import serial

def start_dosenet():
    os.system('sudo bash /home/pi/dosenet-raspberrypi/pocket.sh start')

def start_D3S():
    os.system('sudo bash /home/pi/dosenet-raspberrypi/D3S.sh start')
    
    
if __name__ == '__main__':
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
    
    p = multiprocessing.Process(target=start_D3S, args=())
    t = multiprocessing.Process(target=start_dosenet, args=())
    try:
        print('Starting D3S script process')
        p.start()
        print('Starting Pocket Geiger script process')
        t.start()
        print('started')
        p.join()
        t.join()
        print('we can reboot here')
    except:
        pass
