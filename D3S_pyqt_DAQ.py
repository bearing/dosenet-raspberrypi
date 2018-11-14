import kromek
import datetime
from pyqtgraph.Qt import QtGui, QtCore
import pyqtgraph as pg
import collections
import numpy as np

class DAQThread(QtCore.QThread):
    """
    Setup a signal to send an object
    (part of class namespace - self.data_signal)
    """
    def __init__(self, interval=1):
        self.spectrum_signal = pg.QtCore.Signal(object)
        self.d3s_interval = interval

    def setup_d3s(self, transport, interval, device):
        self.d3s_interval = interval
        self.d3s_devs = self.get_d3s_devs(transport, device)
        if len(self.d3s_devs) > 1:
            print('[GUI] More than 1 D3S found:')
            for d in self.d3s_devs:
                print('    ', d)
            print('[GUI] Only using first:', self.d3s_devs[0])
            self.d3s_devs = self.d3s_devs[0:1]
        self.d3s_controller = self.get_d3s_controller(self.d3s_devs, interval)

    def run(self):
        """
        Main loop. Thread run override (via thread.start())
        """
        # d3s device config
        d3s_devs = self.get_d3s_devs(transport='usb')
        # save file
        t = '{}'.format(
            datetime.datetime.now()).replace(
            ':', '_').replace(
            '.', '_').replace(
            ' ', '_')
        i = 0
        with open('d3slog_{}.csv'.format(t), 'w') as csv_file:
            with self.get_d3s_controller(d3s_devs, self.d3s_interval) as d3s_controller:
                for reading in d3s_controller.read():
                    print('Reading {}'.format(reading))
                    r = self.parse_d3s_reading(reading)
                    print('[{:.2f}] {}: {} cnts'.format(
                        r['timestamp'], r['serial'], r['spectrum'].sum()))

                    # Send spectrum as array object through signal
                    self.spectrum_signal.emit(r['spectrum'])

                    # Save to file
                    if i == 0:
                        csv_file.write(
                            'serial,timestamp,{}\n'.format(','.join(
                                np.arange(len(r['spectrum'])).astype(str))))
                    csv_file.write('{},{:.6f},{}\n'.format(
                        r['serial'],
                        r['timestamp'],
                        ','.join(list(r['spectrum'].astype(str)))))
                    i += 1

    def get_d3s_devs(self, transport='any', device='all'):
        """
        From Invincea + PSI to find D3S devices
        """
        if transport == 'any':
            devs = kromek.discover()
        else:
            devs = kromek.discover(transport)
        print('Discovered {}'.format(devs))
        filtered = []
        for dev in devs:
            if device == 'all' or dev[0] in device:
                filtered.append(dev)
        devs = filtered
        if len(devs) <= 0:
            assert False, 'No D3S device found!'
        return devs


    def get_d3s_controller(self, devs, interval=1):
        """
        Get controller object for >= 1 D3S devices

        Cleanup with:
            controller.stop_collector(serial)
        """
        return kromek.Controller(devs, int(interval))


    def parse_d3s_reading(self, reading):
        data = collections.OrderedDict()
        data['serial'] = reading[0]
        data['timestamp'] = float(reading[1])
        data['r2'] = reading[2]
        data['r3'] = reading[3]
        data['spectrum'] = np.array(reading[4])
        return data
