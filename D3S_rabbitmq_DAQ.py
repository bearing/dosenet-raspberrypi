from globalvalues import RPI
if RPI:
    import RPi.GPIO as GPIO

import time
import traceback
import argparse
import kromek
import numpy as np
import signal
import pika
import sys
import json
import csv

sys.stdout.flush()

from auxiliaries import set_verbosity
#from sender import ServerSender
#from data_handler_d3s import Data_Handler_D3S
from data_handlers import Data_Handler_D3S
# import spectra_fitter

from globalvalues import DEFAULT_LOGFILE_D3S
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
                 interval=1,
                 count=0,
                 transport='usb',
                 device='all',
                 log_bytes=False,
                 verbosity=None,
                 datalog=None,
                 datalogflag=False,
                 test=None,
                 logfile=None,
                 log=False,
                 running=False
                 ):

        self.sensor_type = 2
        self.running = running
        self.post_data = True
        self.test = True

        self.total = None
        self.lst = None
        self.create_structures = True

        self.interval = interval

        self.count = count

        self.config = None
        self.publickey = None

        self.transport = transport
        self.device = device
        self.log_bytes = log_bytes

        self.datalog = datalog
        self.datalogflag = datalogflag

        self.a_flag()
        self.d_flag()
        self.make_data_log(self.datalog)

        self.handle_input(
            log, logfile, verbosity, interval)

        self.data_handler = Data_Handler_D3S(
            manager=self,
            verbosity=verbosity,
            logfile=self.logfile)


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
        Sets up logging, verbosity, interval
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
                        serial = reading[0]
                        dev_count = reading[1]
                        if serial not in done_devices:
                            this_start, this_end = self.get_interval(
                                time.time() - self.interval)

                            print('Checking post status')
                            self.handle_spectra(
                                this_start, this_end, reading[4])
                            self.post_spectra(reading[4])
                        if dev_count >= self.count > 0:
                            done_devices.add(serial)
                            controller.stop_collector(serial)
                        if len(done_devices) >= len(devs):
                            break
        except KeyboardInterrupt:
            print('\nKeyboardInterrupt: stopping Manager run')
            self.takedown()
        except SystemExit:
            print('\nSystemExit: taking down Manager')
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
                writer = csv.writer(f, delimiter=',')
                writer.writerow(spectra)
                self.vprint(
                    2, 'Writing spectra to data log at {}'.format(file))

    def calibration_log(self, file, spectra):
        """
        Dummy method for compatibility.
        """

    def handle_spectra(self, this_start, this_end, spectra):
        """
        Get spectra from sensor, display text, send to log.
        """

        self.data_handler.main(
            self.datalog, this_start, this_end,
            calibrationlog=None, spectra= spectra)

    def post_spectra(self, spectra):
        # Check for server commands and change local state var accordingly
        msg = self.receive()
        if msg=='STOP':
            self.post_data = False
        if msg=='START':
            self.post_data = True
        if msg=='EXIT':
            self.takedown()

        print('Post data status: {}'.format(self.post_data))
        sys.stdout.flush()
        if self.post_data:
            print('Sending data to GUI')
            self.send_data(spectra)


    def send_data(self, data):
        connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
        channel = connection.channel()
        channel.queue_declare(queue='toGUI')
        message = {'id': 'Radiation', 'data': data}
        #print("Sending {}".format(data))
        channel.basic_publish(exchange='',routing_key='toGUI',body=json.dumps(message))
        connection.close()


    def receive(self):
        connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
        channel = connection.channel()
        channel.queue_declare(queue='fromGUI')
        method_frame, header_frame, body = channel.basic_get(queue='fromGUI')
        if body is not None:
            message = json.loads(body)
            if message['id']=='Radiation':
                channel.basic_ack(delivery_tag=method_frame.delivery_tag)
                connection.close()
                return message['cmd']
            else:
                connection.close()
                return None
        else:
            connection.close()
            return None


    def takedown(self):
        """
        Sets self.running to False and deletes self. Also turns off LEDs
        """
        GPIO.cleanup()

        self.running = False
        self.data_handler.send_all_to_backlog()

        del(self)
        sys.exit(0)

    @classmethod
    def from_argparse(cls):
        parser = argparse.ArgumentParser()
        parser.add_argument('--datalog', '-d', default=None)
        parser.add_argument(
            '--datalogflag', '-a', action='store_true', default=False)
        parser.add_argument('--verbosity', '-v', type=int, default=None)
        parser.add_argument('--test', '-t', action='store_true', default=None)
        parser.add_argument('--transport', '-n', default= 'usb')
        parser.add_argument('--interval', '-i', type=int, default=5)
        parser.add_argument('--count', '-o', dest='count', default=0)
        parser.add_argument('--device', '-e', dest='device', default='all')
        parser.add_argument(
            '--log-bytes', '-b', dest='log_bytes', default=False,
            action='store_true')
        parser.add_argument('--log', '-l', action='store_true', default=False)
        parser.add_argument('--logfile', '-f', type=str, default=None)

        args = parser.parse_args()
        arg_dict = vars(args)
        mgr = Manager_D3S(**arg_dict)

        return mgr

def main():

    mgr = Manager_D3S.from_argparse()

    idx = 0
    while True:
        # Look for messages from GUI every 10 ms
        msg = mgr.receive()
        print("received msg {}: {}".format(idx, msg))
        sys.stdout.flush()
        idx = idx + 1

        # If START is sent, begin running daq
		#    - collect data every second
		#    - re-check for message from GUI
        if msg == 'START':
            try:
                mgr.run()
            except:
                if mgr.logfile:
                    # print exception info to logfile
                    with open(mgr.logfile, 'a') as f:
                        traceback.print_exc(15, f)
                # regardless, re-raise the error which will print to stderr
                raise

        time.sleep(.5)

if __name__ == '__main__':

    '''
    Execute the main method with argument parsing enabled.
    '''
    main()
