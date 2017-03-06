from manager import Manager
from manager_D3S import Manager_D3S
import os
import multiprocessing

def start_dosenet():
    os.system('./dosenet.sh start')
def start_D3S():
    os.system('./D3S.sh start')
    
    
if __name__ == '__main__':
    p = multiprocessing.Process(target=start_D3S, args=())
    t = multiprocessing.Process(target=start.dosenet, args=())
    try:
        print('starting')
        p.start()
        t.start()
        print('started')
    except:
        pass
