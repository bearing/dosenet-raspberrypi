from manager import Manager
from manager_D3S import Manager_D3S
import os
import multiprocessing

def start_dosenet():
    os.system('./home/pi/dosenet-raspberrypi/dosenet.sh start')

def start_D3S():
    os.system('./home/pi/dosenet-raspberrypi/D3S.sh start')
    
    
if __name__ == '__main__':
    os.system('sudo service ntp stop')
    os.system('sudo timeout 60s ntpd -gq')
    os.system('sudo service ntp start')

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
