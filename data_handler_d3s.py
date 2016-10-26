from auxiliaries import datetime_from_epoch
from auxiliaries import set_verbosity
from globalvalues import ANSI_RESET, ANSI_YEL, ANSI_GR, ANSI_RED
from globalvalues import DEFAULT_DATA_BACKLOG_FILE_D3S
from collections import deque
import socket
import time
import ast
import os

SPECTRA_DISPLAY_TEXT = (
    '{{time}}: {yellow} {{total_counts}} {reset}' +
    '{green} total counts from {reset}' +
    ' ({{start_time}} to {{end_time}})').format(
    yellow=ANSI_YEL, reset=ANSI_RESET, green = ANSI_GR)
strf = '%H:%M:%S'

class Data_Handler_D3S(object):

    def __init__(self,
                 manager=None,
                 verbosity=1,
                 logfile=None,
                 network_led=None,
                 ):
               
        self.v = verbosity
        if manager and logfile is None:
            set_verbosity(self, logfile=manager.logfile)
        else:
            set_verbosity(self, logfile=logfile)

    
        self.manager = manager
        self.queue = deque('')
        
        self.blink_period_s = 1.5
        self.led = network_led
    
    def test_send(self, spectra):
        """
        Test Mode
        """
        self.vprint(
            1, ANSI_RED + " * Test mode, not sending to server * " +
            ANSI_RESET)
            
    def no_config_send(self, spectra):
        """
        Configuration file not present
        """
        self.vprint(1, "Missing config file, not sending to server")

    def no_publickey_send(self, spectra):
        """
        Publickey not present
        """
        self.vprint(1, "Missing public key, not sending to server")
        
    def send_to_memory(self, spectra):
        """
        Network is not up
        """
        if self.led:
            self.led.start_blink(interval=self.blink_period_s)
        self.send_to_queue(spectra)
        self.vprint(1, "Network down, saving to queue in memory")

    def regular_send(self, this_end, spectra):
        """
        Normal send
        """
        if self.led:
            if self.led.blinker:
                self.led.stop_blink()
            self.led.on()
        self.manager.sender.send_spectra_new_D3S(this_end, spectra)
        if self.queue:
            self.vprint(1, "Flushing memory queue to server")
        while self.queue:
            trash = self.queue.popleft()
            self.manager.sender.send_spectra_new_D3S(
                trash[0], trash[1])

    def send_all_to_backlog(self, path=DEFAULT_DATA_BACKLOG_FILE_D3S):
        if self.queue:
            self.vprint(1, "Flushing memory queue to backlog file")
            with open(path, 'a') as f:
                while self.queue:
                    f.write('{0}, '.format(self.queue.popleft()))

    def send_to_queue(self, spectra):
        """
        Adds the time and spectra to the deque object.
        """
        time_string = time.time()
        self.queue.append([time_string, spectra])

    def backlog_to_queue(self, path=DEFAULT_DATA_BACKLOG_FILE_D3S):
        """
        Sends data in backlog to queue and deletes the backlog
        """
        if os.path.isfile(path):
            self.vprint(2, "Flushing backlog file to memory queue")
            with open(path, 'r') as f:
                data = f.read()
            data = ast.literal_eval(data)
            for i in data:
                self.queue.append([i[0], i[1]])
            print(self.queue)
            os.remove(path)

    def main(self, datalog, calibrationlog, spectra, this_start, this_end):
        """
        Determines how to handle the spectra data.
        """
        start_text = datetime_from_epoch(this_start).strftime(strf)
        end_text = datetime_from_epoch(this_end).strftime(strf)

        self.vprint(
            1, SPECTRA_DISPLAY_TEXT.format(
                time=datetime_from_epoch(time.time()),
                total_counts=sum(spectra),
                start_time=start_text,
                end_time=end_text))

        self.manager.data_log(datalog, spectra)
        self.manager.calibration_log(calibrationlog, spectra)

        if self.manager.test:
            # for testing the memory queue
            self.send_to_memory(spectra)
        elif not self.manager.config:
            self.no_config_send(spectra)
        elif not self.manager.publickey:
            self.no_publickey_send(spectra)
        else:
            try:
                self.regular_send(this_end, spectra)
            except (socket.gaierror, socket.error, socket.timeout) as e:
                if e == socket.gaierror:
                    if e[0] == socket.EAI_AGAIN:
                        # TCP and UDP
                        # network is down, but NetworkStatus didn't notice yet
                        # (resolving DNS like dosenet.dhcp.lbl.gov)
                        self.vprint(
                            1, 'Failed to send packet! Address resolution error')
                    else:
                        self.vprint(1, 'Failed to send packet! Address error: ' +
                                    '{}: {}'.format(*e))
                elif e == socket.error:
                    if e[0] == errno.ECONNREFUSED:
                        # TCP
                        # server is not accepting connections
                        self.vprint(1, 'Failed to send packet! Connection refused')
                    elif e[0] == errno.ENETUNREACH:
                        # TCP and UDP
                        # network is down, but NetworkStatus didn't notice yet
                        # (IP like 131.243.51.241)
                        self.vprint(
                            1, 'Failed to send packet! Network is unreachable')
                    else:
                        # consider handling errno.ECONNABORTED, errno.ECONNRESET
                        self.vprint(1, 'Failed to send packet! Socket error: ' +
                                    '{}: {}'.format(*e))
                elif e == socket.timeout:
                    # TCP
                    self.vprint(1, 'Failed to send packet! Socket timeout')
                self.send_to_memory(spectra)
