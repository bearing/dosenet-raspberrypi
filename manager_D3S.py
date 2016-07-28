import argparse
import kromek
import numpy as np

import time

from globalvalues import DEFAULT_INTERVAL_NORMAL_D3S

from auxiliaries import set_verbosity

class Manager_D3S(object):
    """
    Master object for D3S device operation. 
    
    Prints out spectra for every interval, stores each spectra, and sums the spectra together. 
    
    Interval is in seconds with the default being 30 seconds.
    """
    
    def __init__(self,
                 interval=None,
                 count=0,
                 transport='usb', 
                 device='all',
                 log_bytes=False,
                 verbosity=None, 
                 ):
    
        self.total = None
        self.lst = None
        self.create_structures = True
        
        self.interval = interval
        self.count = count
        
        self.transport = transport
        self.device = device
        self.log_bytes = log_bytes
        
        self.handle_input(verbosity, interval)
            
    def handle_input(self, verbosity, interval):
        
        if verbosity is None:
            verbosity = 1
        self.v = verbosity
        set_verbosity(self)
        
        if interval is None:
            self.vprint(
                2, "No interval given, using interval at 30 seconds")
            interval = DEFAULT_INTERVAL_NORMAL_D3S
        self.interval = interval
            
    def run(self):
        """
        Main method. Currently also stores and sum the spectra as well. 
        
        Current way to stop is only using a keyboard interrupt.
        """
        
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
                    x = time.time()              
                else:
                    self.total += np.array(reading[4])
                    self.lst = np.concatenate((self.lst, [np.array(reading[4])]))
                    print time.time() - x
                    x = time.time()
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
        parser.add_argument('--transport', '-t', dest='transport', default='usb')
        parser.add_argument('--interval', '-i', type=int, default=None)
        parser.add_argument('--count', '-c', dest='count', default=0)
        parser.add_argument('--device', '-d', dest='device', default='all')
        parser.add_argument('--log-bytes', '-b', dest='log_bytes', default=False, action='store_true')
        args = parser.parse_args()
        
        arg_dict = vars(args)
        mgr = Manager_D3S(**arg_dict)
        return mgr
    
if __name__ == '__main__':
    mgr = Manager_D3S.from_argparse()
    mgr.run()
