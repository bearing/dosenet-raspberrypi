import argparse
import kromek
import numpy as np

class Manager_D3S(object):
    
    def __init__(self,
                 interval=None,
                 count=0,
                 transport='any', 
                 device='all',
                 log_bytes=False,
                 ):
    
        self.total = None
        self.lst = None
        self.create_structures = True
        
        self.interval = interval
        self.count = count
        
        self.transport = transport
        self.device = device
        self.log_bytes = log_bytes
        
        if self.interval == None:
            self.interval = 30
            
    def run(self):
        if self.transport == 'any':
            devs = kromek.discover()
        else:
            devs = kromek.discover(self.transport)
        print 'Discovered %s' % devs
        if len(devs) <= 0:
            return
        
        filtered = []
        
        for dev in devs:
            if self.device == 'all' or dev[0] in self.device:
                filtered.append(dev)
    
        devs = filtered
        if len(devs) <= 0:
            return

        done_devices = set()
        with kromek.Controller(devs, self.interval) as controller:
            for reading in controller.read():
                if self.create_structures:
                    self.total = np.array(reading[4])
                    self.lst = np.array([reading[4]])
                    self.create_structures = False
                else:
                    self.total += np.array(reading[4])
                    self.lst = np.concatenate((self.lst, [np.array(reading[4])]))
                serial = reading[0]
                dev_count = reading[1]
                if serial not in done_devices:
                    print reading[4]
                if dev_count >= self.count > 0:
                    done_devices.add(serial)
                    controller.stop_collector(serial)
                if len(done_devices) >= len(devs):
                    break
    
    @classmethod
    def from_argparse(cls):
        parser = argparse.ArgumentParser()
        parser.add_argument('--transport', '-t', dest='transport', default='any')
        parser.add_argument('--interval', '-i', dest='interval', default=None)
        parser.add_argument('--count', '-c', dest='count', default=0)
        parser.add_argument('--device', '-d', dest='device', default='all')
        parser.add_argument('--log-bytes', '-b', dest='log_bytes', default=False, action='store_true')
        args = parser.parse_args()
        
        arg_dict = vars(args)
        mgr = Manager_D3S(**arg_dict)
        return mgr
    
if __name__ == '__main__':
    mgr = Manager_D3S()
    mgr.run()
