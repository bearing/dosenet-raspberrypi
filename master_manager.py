#!/usr/bin/env python
import os
import multiprocessing
import serial

def start_dosenet():
    os.system('sudo /home/pi/dosenet-raspberrypi/dosenet.sh start')

def start_D3S():
    os.system('sudo /home/pi/dosenet-raspberrypi/D3S.sh start')
    
    
if __name__ == '__main__':
    os.system('sudo service ntp stop')
    os.system('sudo timeout 60s ntpd -gq')
    os.system('sudo service ntp start')

    ser = serial.Serial('/dev/ttyACM0')
    ser.flushInput()
    ser.Close()
    
    p = multiprocessing.Process(target=start_D3S, args=())
    t = multiprocessing.Process(target=start_dosenet, args=())
    try:
        print('starting')
        p.start()
        t.start()
        print('started')
        p.join()
        t.join()
        print('we can reboot here')
    except:
        pass
