from globalvalues import RPI
if RPI:
    import RPi.GPIO as GPIO

import time
import traceback
import argparse
import kromek
import numpy as np
import signal
import sys


from auxiliaries import set_verbosity
#from sender import ServerSender
from data_handler_d3s import Data_Handler_D3S
from Real_Time_Spectra import Real_Time_Spectra
# import spectra_fitter

from globalvalues import DEFAULT_CALIBRATIONLOG_D3S, DEFAULT_LOGFILE_D3S
from globalvalues import DEFAULT_CALIBRATIONLOG_TIME
from globalvalues import DEFAULT_DATALOG_D3S

def signal_term_handler(signal, frame):
    # If SIGTERM signal is intercepted, the SystemExit exception routines
    #   get run

    print('Got Sigterm!')

    sys.exit(0)

signal.signal(signal.SIGTERM, signal_term_handler)


class Manager_D3S(object):
    """
    Master object for D3S device operation.
    Prints out spectra for every interval, stores each spectra, and
    sums the spectra together.
    Interval is in seconds with the default being 30 seconds.
    """

    def __init__(self,
                 interval=5,
                 maxspectra=20,
                 count=0,
                 transport='any',
                 device='all',
                 log_bytes=False,
                 verbosity=None,
                 datalog=None,
                 datalogflag=False,
                 calibrationlog=None,
                 calibrationlogflag=False,
                 calibrationlogtime=None,
                 test=None,
                 logfile=None,
                 log=False,
                 running=False,
                 plot=True
                 ):

        self.running = running

        self.total = None
        self.lst = None
        self.create_structures = True

        self.interval = interval
        self.maxspectra = maxspectra
        self.count = count
        self.dev_count = 0
        self.serial = 0

        self.config = None
        self.publickey = None

        self.transport = transport
        self.device = device
        self.log_bytes = log_bytes

        self.calibrationlog = calibrationlog
        self.calibrationlogflag = calibrationlogflag
        self.c_timer = 0
        self.calibrationlogtime = calibrationlogtime

        self.z_flag()
        self.y_flag()
        self.x_flag()
        self.make_calibration_log(self.calibrationlog)

        self.datalog = datalog
        self.datalogflag = datalogflag

        self.a_flag()
        self.d_flag()
        self.make_data_log(self.datalog)

        self.test = test

        self.handle_input(
            log, logfile, verbosity, interval)
        self.plot = plot

        self.data_handler = Data_Handler_D3S(
            manager=self,
            verbosity=self.v,
            logfile=self.logfile)
        # self.sender = ServerSender(
        #     manager=self,
        #     mode=sender_mode,
        #     port=port,
        #     verbosity=self.v,
        #     logfile=self.logfile,)
        # DEFAULT_UDP_PORT and DEFAULT_TCP_PORT are assigned in sender

        self.data_handler.backlog_to_queue()

        print('creating plotter')
        self.rt_plot = Real_Time_Spectra(
            manager=self,
            verbosity=self.v)


    def z_flag(self):
        """
        Checks if the -z from_argparse is called.
        If it is called, sets the path of the calibration-log to
        DEFAULT_CALIBRATIONLOG_D3S.
        """
        if self.calibrationlogflag:
            self.calibrationlog = DEFAULT_CALIBRATIONLOG_D3S

    def y_flag(self):
        """
        Checks if the -y from_argparse is called.
        If it is called, sets calibrationlogflag to True.
        Also sets calibrationlogtime to DEFAULT_CALIBRATIONLOG_TIME.
        """
        if self.calibrationlog:
            self.calibrationlogflag = True
            self.calibrationlogtime = DEFAULT_CALIBRATIONLOG_TIME

    def x_flag(self):
        """
        Checks if -x is called.
        If it is called, sets calibrationlogflag to True.
        Also sets calibrationlog to DEFAULT_CALIBRATIONLOG_D3S.
        """
        if self.calibrationlogtime and (
                self.calibrationlogtime != DEFAULT_CALIBRATIONLOG_TIME):
            self.calibrationlog = DEFAULT_CALIBRATIONLOG_D3S
            self.calibrationlogflag = True

    def make_calibration_log(self, file):
        if self.calibrationlogflag:
            with open(file, 'a') as f:
                pass

    def a_flag(self):
        """
        Checks if the -a from_argparse is called.
        If it is called, sets the path of the data-log to
        DEFAULT_DATALOG_D3S.
        """
        if self.datalogflag:
            self.datalog = DEFAULT_DATALOG_D3S

    def d_flag(self):
        """
        Checks if the -d from_argparse is called.
        If it is called, sets datalogflag to True.
        """
        if self.datalog:
            self.datalogflag = True

    def make_data_log(self, file):
        if self.datalogflag:
            with open(file, 'a') as f:
                pass

    def handle_input(self, log, logfile, verbosity, interval):
        """
        Sets up logging, verbosity, interval, config, and publickey
        """

        # resolve logging defaults
        if log and logfile is None:
            # use default file if logging is enabled
            logfile = DEFAULT_LOGFILE_D3S
        if logfile and not log:
            # enable logging if logfile is specified
            #   (this overrides a log=False input which wouldn't make sense)
            log = True
        if log:
            self.logfile = logfile
        else:
            self.logfile = None

        if verbosity is None:
            verbosity = 1
        self.v = verbosity
        set_verbosity(self, logfile=logfile)

        if log:
            self.vprint(1, '')
            self.vprint(1, 'Writing to logfile at {}'.format(self.logfile))
        self.running = True

        if interval is None:
            self.vprint(
                2, "No interval given, using interval at 30 seconds")
            interval = DEFAULT_INTERVAL_NORMAL_D3S

        self.interval = int(interval)

    def close(self, plot_id):
        self.rt_plot.close(plot_id)

    def run(self):
        """
        Main method. Currently also stores and sum the spectra as well.
        Current way to stop is only using a keyboard interrupt.
        """

        if self.transport == 'any':
            devs = kromek.discover()
        else:
            devs = kromek.discover(self.transport)

        print('Discovered %s' % devs)

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
        try:
            while self.running:

                print("Plot_manager.run: getting data")
                with kromek.Controller(devs, self.interval) as controller:
                    for reading in controller.read():
                        if self.create_structures:
                            self.total = np.array(reading[4])
                            self.lst = np.array([reading[4]])
                            self.create_structures = False
                        else:
                            self.total += np.array(reading[4])
                            self.lst = np.concatenate(
                                (self.lst, [np.array(reading[4])]))
                        self.serial = reading[0]
                        print("Serial and its type:", self.serial)
                        self.dev_count = reading[1]
                        print("Count and its type:", self.dev_count)
                        if self.serial not in done_devices:
                            this_start, this_end = self.get_interval(
                                time.time() - self.interval)

                            self.handle_spectra(
                                this_start, this_end, reading[4])
                            self.rt_plot.make_image()

                        if self.dev_count >= self.count > 0:
                            done_devices.add(serial)
                            controller.stop_collector(serial)
                        if len(done_devices) >= len(devs):
                            break
        except KeyboardInterrupt:
            self.vprint(1, '\nKeyboardInterrupt: stopping Manager run')
            self.takedown()
        except SystemExit:
            self.vprint(1, '\nSystemExit: taking down Manager')
            self.takedown()

    def get_interval(self, start_time):
        """
        Return start and end time for interval, based on given start_time.
        """
        end_time = start_time + self.interval
        return start_time, end_time

    def data_log(self, file, spectra):
        """
        Writes spectra to data-log.
        """
        if self.datalogflag:
            with open(file, 'a') as f:
                f.write('{0}, '.format(spectra))
                self.vprint(
                    2, 'Writing spectra to data log at {}'.format(file))

    def calibration_log(self, file, spectra):
        """
        Writes spectra to calibration-log.
        """
        if self.calibrationlogflag:
            with open(file, 'a') as f:
                f.write('{0}, '.format(spectra))
                self.vprint(
                    2, 'Writing spectra to calibration log at {}'.format(file))
            self.c_timer += self.interval
            if self.c_timer >= self.calibrationlogtime:
                self.vprint(1, 'Calibration Complete')
                self.takedown()

    def plot_waterfall(self, plot_id):
        """Wrapper around waterfall plotter in Real_Time_Spectra class"""

        self.rt_plot.plot_waterfall(plot_id)

    def plot_spectrum(self,plot_id):
        """Wrapper around spectrum plotter in Real_Time_Spectra class"""
        count = self.dev_count
        time = self.serial
        self.rt_plot.plot_sum(plot_id,count,time)


    def plot_fitter(self):
        """
        Wrapper around spectrum-fitter data acquisition plotter in
        spectra_fitter class
        """

        total_time=self.interval*self.maxspectra
        times = np.linspace(self.interval,total_time + 1,self.interval)
        spectra_fitter.main(self.rt_plot.sum_data, times)

    def handle_spectra(self, this_start, this_end, spectra):
        """
        Get spectra from sensor, display text, send to server.
        """

        self.rt_plot.add_data(self.rt_plot.queue, spectra, self.maxspectra)

        if self.plot:

            '''
            Plot the data.
            '''
            self.plot_waterfall(1)
            self.plot_spectrum(2)
            # self.plot_fitter()

            '''
            Uncomment 3 lines below to plot the spectra fitter plots.
            '''
        else:
            self.data_handler.main(
                self.datalog, self.calibrationlog, spectra, this_start, this_end)

    def takedown(self):
        """
        Sets self.running to False and deletes self. Also turns off LEDs
        """
        GPIO.cleanup()

        self.running = False
        self.data_handler.send_all_to_backlog()

        
        del(self)
        
    @classmethod
    def from_argparse(cls):
        parser = argparse.ArgumentParser()
        parser.add_argument('--datalog', '-d', default=None)
        parser.add_argument(
            '--datalogflag', '-a', action='store_true', default=True)
        parser.add_argument('--verbosity', '-v', type=int, default=None)
        parser.add_argument('--test', '-t', action='store_true', default=None)
        parser.add_argument('--transport', '-n', default= 'usb')
        parser.add_argument('--interval', '-i', type=int, default=5)
        parser.add_argument('--maxspectra', '-s', default=20)
        parser.add_argument('--count', '-o', dest='count', default=0)
        parser.add_argument('--device', '-e', dest='device', default='all')
        parser.add_argument(
            '--log-bytes', '-b', dest='log_bytes', default=False,
            action='store_true')
        parser.add_argument('--log', '-l', action='store_true', default=False)
        parser.add_argument('--logfile', '-f', type=str, default=None)
        parser.add_argument('--calibrationlogtime', '-x', type=int, default=None)
        parser.add_argument('--calibrationlog', '-y', default=None)
        parser.add_argument(
            '--calibrationlogflag', '-z', action='store_true', default=False)
        parser.add_argument('--plot', '-p', action='store_true', default=True)

        args = parser.parse_args()
        arg_dict = vars(args)
        mgr = Manager_D3S(**arg_dict)

        return mgr

def main():

    mgr = Manager_D3S.from_argparse()

    try:
        mgr.run()
    except:
        if mgr.logfile:
            # print exception info to logfile
            with open(mgr.logfile, 'a') as f:
                traceback.print_exc(15, f)
        # regardless, re-raise the error which will print to stderr
        raise

if __name__ == '__main__':

    '''
    Execute the main method with argument parsing enabled.
    '''
    main()
