from auxiliaries import datetime_from_epoch
from auxiliaries import set_verbosity
from globalvalues import ANSI_RESET, ANSI_YEL, ANSI_GR, ANSI_RED
from globalvalues import DEFAULT_DATA_BACKLOG_FILE
from collections import deque
import socket
import time
import ast
import os

CPM_DISPLAY_TEXT = (
    '{{time}}: {yellow} {{counts}} cts{reset}' +
    ' --- {green}{{cpm:.2f}} +/- {{cpm_err:.2f}} cpm{reset}' +
    ' ({{start_time}} to {{end_time}})').format(
    yellow=ANSI_YEL, reset=ANSI_RESET, green=ANSI_GR)
strf = '%H:%M:%S'


class Data_Handler(object):
    """
    Object for sending data to server.

    Also handles writing to datalog and
    storing to memory.
    """

    def __init__(self,
                 manager=None,
                 verbosity=1,
                 logfile=None):

        self.v = verbosity
        if manager and logfile is None:
            set_verbosity(self, logfile=manager.logfile)
        else:
            set_verbosity(self, logfile=logfile)

        self.manager = manager
        self.queue = deque('')

    def test_send(self, cpm, cpm_err):
        """
        Test Mode
        """
        self.vprint(
            1, ANSI_RED + " * Test mode, not sending to server * " +
            ANSI_RESET)

    def no_config_send(self, cpm, cpm_err):
        """
        Configuration file not present
        """
        self.vprint(1, "Missing config file, not sending to server")

    def no_publickey_send(self, cpm, cpm_err):
        """
        Publickey not present
        """
        self.vprint(1, "Missing public key, not sending to server")

    def no_network_send(self, cpm, cpm_err):
        """
        Network is not up
        """
        if self.manager.protocol == 'new':
            self.send_to_queue(cpm, cpm_err)
            self.vprint(1, "Network down, saving to queue in memory")
        else:
            self.vprint(1, "Network down, not sending to server")

    def regular_send(self, this_end, cpm, cpm_err):
        """
        Normal send
        """
        try:
            if self.manager.protocol == 'new':
                self.manager.sender.send_cpm_new(this_end, cpm, cpm_err)
                if self.queue:
                    self.vprint(1, "Flushing memory queue to server")
                while self.queue:
                    trash = self.queue.popleft()
                    self.manager.sender.send_cpm_new(
                        trash[0], trash[1], trash[2])
            else:
                self.manager.sender.send_cpm(cpm, cpm_err)
        except socket.error:
            if self.manager.protocol == 'new':
                self.send_to_queue(cpm, cpm_err)
                self.vprint(1, "Socket error: saving to queue in memory")
            else:
                self.vprint(1, "Socket error: data not sent")

    def send_all_to_backlog(self, path=DEFAULT_DATA_BACKLOG_FILE):
        if self.manager.protocol == 'new':
            if self.queue:
                self.vprint(1, "Flushing memory queue to backlog file")
                with open(path, 'a') as f:
                    while self.queue:
                        f.write('{0}, '.format(self.queue.popleft()))

    def send_to_queue(self, cpm, cpm_err):
        """
        Adds the time, cpm, and cpm_err to the deque object.
        """
        if self.manager.protocol == 'new':
            time_string = time.time()
            self.queue.append([time_string, cpm, cpm_err])

    def backlog_to_queue(self, path=DEFAULT_DATA_BACKLOG_FILE):
        """
        Sends data in backlog to queue and deletes the backlog
        """
        if self.manager.protocol == 'new':
            if os.path.isfile(path):
                self.vprint(2, "Flushing backlog file to memory queue")
                with open(path, 'r') as f:
                    data = f.read()
                data = ast.literal_eval(data)
                for i in data:
                    self.queue.append([i[0], i[1], i[2]])
                print(self.queue)
                os.remove(path)

    def main(self, datalog, cpm, cpm_err, this_start, this_end, counts):
        """
        Determines how to handle the cpm data.
        """
        start_text = datetime_from_epoch(this_start).strftime(strf)
        end_text = datetime_from_epoch(this_end).strftime(strf)

        self.vprint(
            1, CPM_DISPLAY_TEXT.format(
                time=datetime_from_epoch(time.time()),
                counts=counts,
                cpm=cpm,
                cpm_err=cpm_err,
                start_time=start_text,
                end_time=end_text))

        self.manager.data_log(datalog, cpm, cpm_err)

        if self.manager.test:
            self.test_send(cpm, cpm_err)
        elif not self.manager.config:
            self.no_config_send(cpm, cpm_err)
        elif not self.manager.publickey:
            self.no_publickey_send(cpm, cpm_err)
        elif not self.manager.network_up:
            self.no_network_send(cpm, cpm_err)
        else:
            self.regular_send(this_end, cpm, cpm_err)
