import socket
import datetime
import time
import ast
import csv
import os
import errno

from auxiliaries import datetime_from_epoch
from auxiliaries import set_verbosity
from globalvalues import DEFAULT_DATA_BACKLOG_FILE
from globalvalues import DEFAULT_DATA_BACKLOG_FILE_D3S
from globalvalues import DEFAULT_DATA_BACKLOG_FILE_AQ
from globalvalues import DEFAULT_DATA_BACKLOG_FILE_CO2
from globalvalues import DEFAULT_DATA_BACKLOG_FILE_WEATHER
from globalvalues import NETWORK_LED_BLINK_PERIOD_S, NETWORK_LED_BLINK_LOST_CONNECTION

from globalvalues import CPM_DISPLAY_TEXT
from globalvalues import SPECTRA_DISPLAY_TEXT
from globalvalues import AQ_PM_DISPLAY_TEXT, AQ_P_DISPLAY_TEXT
from globalvalues import CO2_DISPLAY_TEXT
from globalvalues import WEATHER_DISPLAY_TEXT
from globalvalues import TIME_DISPLAY_TEXT
from globalvalues import SINGLE_BREAK_LINE, DOUBLE_BREAK_LINE

from globalvalues import FLUSH_PAUSE_S
from globalvalues import strf
from collections import deque

class Data_Handler(object):
    """
    Main Data Handler class that deals with the generic
    data from any of the sensors.

    The more specifc data handling processes are dealt with in
    the sub-classes below.
    """

    def __init__(self,
                 manager=None,
                 verbosity=1,
                 logfile=None,
                 ):
        self.send_fail = False

        self.v = verbosity
        if manager and logfile is None:
            set_verbosity(self, logfile=manager.logfile)
        else:
            set_verbosity(self, logfile=logfile)

        self.first_run = True

        self.manager = manager
        self.queue = deque('')

    def test_send(self, **kwargs):
        """
        Test mode
        """
        self.vprint(
            1, ANSI_RED + " * Test mode, not sending to server * " +
            ANSI_RESET)

    def no_config_send(self, **kwargs):
        """
        Configuration file not present
        """
        self.vprint(1, "Missing config file, not sending to server")

    def no_publickey_send(self, **kwargs):
        """
        Publickey not present
        """
        self.vprint(1, "Missing public key, not sending to server")

    def send_to_memory(self, **kwargs):
        """
        Network is not up
        """
        self.send_to_queue(**kwargs)
        self.vprint(1, "Network down, saving to queue in memory")

    def regular_send(self, this_end, **kwargs):
        """
        Normal send. Socket errors are handled in the main method.
        """
        if self.manager.sensor_type == 1:
            cpm, cpm_err = kwargs.get('cpm'), kwargs.get('cpm_err')
            if self.led and self.first_run:
                self.first_run = False
                if self.led.blinker:
                    self.led.stop_blink()
                self.led.on()
            self.manager.sender.send_cpm_new(this_end, cpm, cpm_err)
            if self.queue:
                self.vprint(1, "Flushing memory queue to server")
                no_error_yet = True
            while self.queue and no_error_yet:
                time.sleep(FLUSH_PAUSE_S)
                trash = self.queue.popleft()
                try:
                    if not self.send_fail and not self.led.is_on:
                        if not self.manager.small_board:
                            self.led.on()
                    self.manager.sender.send_cpm_new(
                        trash[0], trash[1], trash[2])
                except (socket.gaierror, socket.error, socket.timeout) as e:
                    if e == socket.gaierror:
                        if e[0] == socket.EAI_AGAIN:
                            # TCP and UDP
                            # network is down,
                            #   but NetworkStatus didn't notice yet
                            # (resolving DNS like dosenet.dhcp.lbl.gov)
                            self.vprint(
                                1, 'Failed to send packet! ' +
                                'Address resolution error')
                        else:
                            self.vprint(
                                1, 'Failed to send packet! Address error: ' +
                                '{}: {}'.format(*e))
                    elif e == socket.error:
                        if e[0] == errno.ECONNREFUSED:
                            # TCP
                            # server is not accepting connections
                            self.vprint(
                                1, 'Failed to send packet! Connection refused')
                        elif e[0] == errno.ENETUNREACH:
                            # TCP and UDP
                            # network is down,
                            #   but NetworkStatus didn't notice yet
                            # (IP like 131.243.51.241)
                            self.vprint(
                                1, 'Failed to send packet! ' +
                                'Network is unreachable')
                        else:
                            # consider handling errno.ECONNABORTED,
                            #   errno.ECONNRESET
                            self.vprint(
                                1, 'Failed to send packet! Socket error: ' +
                                '{}: {}'.format(*e))
                    elif e == socket.timeout:
                        # TCP
                        self.vprint(1, 'Failed to send packet! Socket timeout')
                    self.send_to_memory(cpm=trash[1], cpm_err=trash[2])
                    no_error_yet = False
                if self.send_fail and no_error_yet:
                    self.send_fail = False
        if self.manager.sensor_type == 2:
            spectra = kwargs.get('spectra')
            self.manager.sender.send_spectra_new_D3S(this_end, spectra)
            if self.queue:
                self.vprint(1, "Flushing memory queue to server")
                while self.queue:
                    trash = self.queue.popleft()
                    self.manager.sender.send_spectra_new_D3S(
                        trash[0], trash[1])

        if self.manager.sensor_type == 3:
            average_data = kwargs.get('average_data')
            self.manager.sender.send_data_new_AQ(this_end, average_data)
            if self.queue:
                self.vprint(1, "Flushing memory queue to server")
                while self.queue:
                    trash = self.queue.popleft()
                    self.manager.sender.send_data_new_AQ(
                        trash[0], trash[1])

        if self.manager.sensor_type == 4:
            average_data = kwargs.get('average_data')
            self.manager.sender.send_data_new_CO2(this_end, average_data)
            if self.queue:
                self.vprint(1, "Flushing memory queue to server")
                while self.queue:
                    trash = self.queue.popleft()
                    self.manager.sender.send_data_new_CO2(
                        trash[0], trash[1])

        if self.manager.sensor_type == 5:
            average_data = kwargs.get('average_data')
            self.manager.sender.send_data_new_weather(this_end, average_data)
            if self.queue:
                self.vprint(1, "Flushing memory queue to server")
                while self.queue:
                    trash = self.queue.popleft()
                    self.manager.sender.send_data_new_weather(
                        trash[0], trash[1])

    def send_all_to_backlog(self, path=None):
        if path == None and self.manager.sensor_type == 1:
            path = DEFAULT_DATA_BACKLOG_FILE
        if path == None and self.manager.sensor_type == 2:
            path = DEFAULT_DATA_BACKLOG_FILE_D3S
        if path == None and self.manager.sensor_type == 3:
            path = DEFAULT_DATA_BACKLOG_FILE_AQ
        if path == None and self.manager.sensor_type == 4:
            path = DEFAULT_DATA_BACKLOG_FILE_CO2
        if path == None and self.manager.sensor_type == 5:
            path = DEFAULT_DATA_BACKLOG_FILE_WEATHER

        if self.manager.sensor_type == 2:
            if self.queue:
                self.vprint(1, "Flushing memory queue to backlog file")
                temp = []
                while self.queue:
                    temp.append(self.queue.popleft())
                with open(path, "ab") as f: # might only work for python 3?
                    writer = csv.writer(f)
                    writer.writerows(temp)
        else:
            if self.queue:
                self.vprint(1, "Flushing memory queue to backlog file")
                with open(path, 'a') as f:
                    while self.queue:
                        f.write('{0}, '.format(self.queue.popleft()))

    def send_to_queue(self, **kwargs):
        """
        Adds the time and spectra to the queue object.
        """
        time_string = time.time()
        if self.manager.sensor_type == 1:
            cpm, cpm_err = kwargs.get('cpm'), kwargs.get('cpm_err')
            self.queue.append([time_string, cpm, cpm_err])
        if self.manager.sensor_type == 2:
            spectra = kwargs.get('spectra')
            self.queue.append([time_string, spectra])
        if self.manager.sensor_type == 3 or \
            self.manager.sensor_type == 4 or self.manager.sensor_type == 5:
            average_data = kwargs.get('average_data')
            self.queue.append([time_string, average_data])

    def backlog_to_queue(self, path=None):
        """
        Sends data in backlog to queue and deletes the backlog
        """
        if self.manager.sensor_type == 1:
            if path == None:
                path = DEFAULT_DATA_BACKLOG_FILE
            if os.path.isfile(path):
                self.vprint(2, "Flushing backlog file to memory queue")
                with open(path, 'r') as f:
                    data = f.read()
                data = ast.literal_eval(data)
                for i in data:
                    self.queue.append([i[0], i[1], i[2]])
                print(self.queue)
                os.remove(path)

        if self.manager.sensor_type == 2:
            if path == None:
                path = DEFAULT_DATA_BACKLOG_FILE_D3S
            if os.path.isfile(path):
                self.vprint(2, "Flushing backlog file to memory queue")
                with open(path, 'rb') as f:
                    reader = csv.reader(f)
                    lst = list(reader)
                for i in lst:
                    timestring = i[0]
                    spectra = i[1]
                    timestring = ast.literal_eval(timestring)
                    spectra = ast.literal_eval(spectra)
                    self.queue.append([timestring, spectra])
                os.remove(path)

        if self.manager.sensor_type in (3, 4, 5):
            if path == None and self.manager.sensor_type == 3:
                path = DEFAULT_DATA_BACKLOG_FILE_AQ
            if path == None and self.manager.sensor_type == 4:
                path = DEFAULT_DATA_BACKLOG_FILE_CO2
            if path == None and self.manager.sensor_type == 5:
                path = DEFAULT_DATA_BACKLOG_FILE_WEATHER
            if os.path.isfile(path):
                self.vprint(2, "Flushing backlog file to memory queue")
                with open(path, 'r') as f:
                    data = f.read()
                data = ast.literal_eval(data)
                for i in data:
                    self.queue.append([i[0], i[1]])
                print(self.queue)
                os.remove(path)

    def main(self, datalog, this_start, this_end, **kwargs):
        """
        Determines how to handle the sensor data.
        """
        start_text = datetime_from_epoch(this_start).strftime(strf)
        end_text = datetime_from_epoch(this_end).strftime(strf)
        date = str(datetime.date.today())
        display_data = []
        if self.manager.sensor_type == 1:
            cpm, cpm_err = kwargs.get('cpm'), kwargs.get('cpm_err')
            counts = kwargs.get('counts')
            self.vprint(
                1, SINGLE_BREAK_LINE)
            self.vprint(
                1, TIME_DISPLAY_TEXT.format(
                    start_time=start_text,
                    end_time=end_text,
                    date=date))
            self.vprint(
                1, CPM_DISPLAY_TEXT.format(
                    counts=counts,
                    cpm=cpm,
                    cpm_err=cpm_err))
            self.vprint(
                1, SINGLE_BREAK_LINE)
            self.manager.data_log(datalog, cpm=cpm, cpm_err=cpm_err)
            display_data = [cpm, cpm_err]

        if self.manager.sensor_type == 2:
            spectra = kwargs.get('spectra')
            calibrationlog = kwargs.get('calibrationlog')
            self.vprint(
                1, SINGLE_BREAK_LINE)
            self.vprint(
                1, TIME_DISPLAY_TEXT.format(
                    start_time=start_text,
                    end_time=end_text,
                    date=date))
            self.vprint(
                1, SPECTRA_DISPLAY_TEXT.format(
                    total_counts=sum(spectra)))
            self.vprint(
                1, SINGLE_BREAK_LINE)

            self.manager.data_log(datalog, spectra=spectra)
            self.manager.calibration_log(calibrationlog, spectra)
            display_data = [sum(spectra)/float(self.manager.interval)]

        if self.manager.sensor_type == 3:
            average_data = kwargs.get('average_data')
            self.vprint(
                1, SINGLE_BREAK_LINE)
            self.vprint(
                1, TIME_DISPLAY_TEXT.format(
                    start_time=start_text,
                    end_time=end_text,
                    date=date))
            for i in range(3):
            	self.vprint(
                    1, AQ_PM_DISPLAY_TEXT.format(
                        variable=self.variables[i],
                        avg_data=average_data[i]))
            for i in range(3, 9):
            	self.vprint(
                    1, AQ_P_DISPLAY_TEXT.format(
                        variable=self.variables[i],
                        avg_data=average_data[i]))
            self.vprint(
                1, SINGLE_BREAK_LINE)

            self.manager.data_log(datalog, average_data=average_data)
            display_data = average_data

        if self.manager.sensor_type == 4:
            average_data = kwargs.get('average_data')
            self.vprint(
                1, SINGLE_BREAK_LINE)
            self.vprint(
                1, TIME_DISPLAY_TEXT.format(
                    start_time=start_text,
                    end_time=end_text,
                    date=date))
            for i in range(len(self.variables)):
                self.vprint(
                    1, CO2_DISPLAY_TEXT.format(
                        variable=self.variables[i],
                        data=average_data[i]))
            self.vprint(
                1, SINGLE_BREAK_LINE)

            self.manager.data_log(datalog, average_data=average_data)
            display_data = average_data

        if self.manager.sensor_type == 5:
            average_data = kwargs.get('average_data')
            self.vprint(
                1, SINGLE_BREAK_LINE)
            self.vprint(
                1, TIME_DISPLAY_TEXT.format(
                    start_time=start_text,
                    end_time=end_text,
                    date=date))
            for i in range(len(self.variables)):
                self.vprint(
                    1, WEATHER_DISPLAY_TEXT.format(
                        variable=self.variables[i],
                        unit=self.variables_units[i],
                        data=average_data[i]))
            self.vprint(
                1, SINGLE_BREAK_LINE)

            self.manager.data_log(datalog, average_data=average_data)
            display_data = average_data

        if self.manager.oled:
            self.manager.oled_send(display_data)

        if self.manager.test:
            if self.manager.sensor_type == 1:
                self.send_to_memory(cpm=cpm, cpm_err=cpm_err)
            elif self.manager.sensor_type == 2:
                self.send_to_memory(spectra=spectra)
            elif self.manager.sensor_type in [3,4,5]:
                self.send_to_memory(average_data=average_data)
        elif not self.manager.config:
            if self.manager.sensor_type == 1:
                self.no_config_send(cpm=cpm, cpm_err=cpm_err)
            elif self.manager.sensor_type == 2:
                self.no_config_send(spectra=spectra)
            elif self.manager.sensor_type in [3,4,5]:
                self.no_config_send(average_data=average_data)
        elif not self.manager.publickey:
            if self.manager.sensor_type == 1:
                self.no_publickey_send(cpm=cpm, cpm_err=cpm_err)
            elif self.manager.sensor_type == 2:
                self.no_publickey_send(spectra=spectra)
            elif self.manager.sensor_type in [3,4,5]:
                self.no_publickey_send(average_data=average_data)

        if not self.manager.test:
            try:
                if self.manager.sensor_type == 1:
                    self.regular_send(this_end, cpm=cpm, cpm_err=cpm_err)
                if self.manager.sensor_type == 2:
                    self.regular_send(this_end, spectra=spectra)
                if self.manager.sensor_type == 3 or \
                    self.manager.sensor_type == 4 or self.manager.sensor_type == 5:
                    self.regular_send(this_end, average_data=average_data)
            except (socket.gaierror, socket.error, socket.timeout) as e:
                if e == socket.gaierror:
                    if e[0] == socket.EAI_AGAIN:
                        # TCP and UDP
                        # network is down, but NetworkStatus didn't notice yet
                        # (resolving DNS like dosenet.dhcp.lbl.gov)
                        self.vprint(
                            1,
                            'Failed to send packet! Address resolution error')
                    else:
                        self.vprint(
                            1, 'Failed to send packet! Address error: ' +
                            '{}: {}'.format(*e))
                elif e == socket.error:
                    if e[0] == errno.ECONNREFUSED:
                        # TCP
                        # server is not accepting connections
                        self.vprint(
                            1, 'Failed to send packet! Connection refused')
                    elif e[0] == errno.ENETUNREACH:
                        # TCP and UDP
                        # network is down, but NetworkStatus didn't notice yet
                        # (IP like 131.243.51.241)
                        self.vprint(
                            1, 'Failed to send packet! Network is unreachable')
                    else:
                        # consider handling errno.ECONNABORTED errno.ECONNRESET
                        self.vprint(
                            1, 'Failed to send packet! Socket error: ' +
                            '{}: {}'.format(*e))
                elif e == socket.timeout:
                    # TCP
                    self.vprint(1, 'Failed to send packet! Socket timeout')
                if self.manager.sensor_type == 1:
                    if self.send_fail:
                        if not self.manager.small_board:
                            self.led.stop_blink()
                            self.led.off()
                    if not self.send_fail:
                        self.send_fail = True
                        if not self.manager.small_board:
                            self.led.start_blink(interval=self.blink_period_lost_connection)
                    self.send_to_memory(cpm=cpm, cpm_err=cpm_err)
                if self.manager.sensor_type == 2:
                    self.send_to_memory(spectra=spectra)
                if self.manager.sensor_type == 3 or \
                    self.manager.sensor_type == 4 or self.manager.sensor_type == 5:
                    self.send_to_memory(average_data=average_data)

class Data_Handler_Pocket(Data_Handler):
    """
    Sub data handler for the Pocket Geiger sensor.

    Any specific variables to this sensor will be
    defined in this sub-class.
    """

    def __init__(self,
                 network_led=None,
                 **kwargs):

        super(Data_Handler_Pocket, self).__init__(**kwargs)

        self.blink_period_s = NETWORK_LED_BLINK_PERIOD_S
        self.blink_period_lost_connection = NETWORK_LED_BLINK_LOST_CONNECTION
        self.led = network_led

class Data_Handler_D3S(Data_Handler):
    """
    Sub data handler for the D3S sensor.

    Any specific variables to this sensor will be
    defined in this sub-class.
    """

    def __init__(self,
                 **kwargs):

        super(Data_Handler_D3S, self).__init__(**kwargs)

class Data_Handler_AQ(Data_Handler):
    """
    Sub data handler for the Air Quality sensor.

    Any specific variables to this sensor will be
    defined in this sub-class.
    """

    def __init__(self,
                 variables=None,
                 **kwargs):

        self.variables = variables

        super(Data_Handler_AQ, self).__init__(**kwargs)

class Data_Handler_CO2(Data_Handler):
    """
    Sub data handler for the CO2 sensor.

    Any specific variables to this sensor will be
    defined in this sub-class.
    """

    def __init__(self,
                 variables=None,
                 **kwargs):

        self.variables = variables

        super(Data_Handler_CO2, self).__init__(**kwargs)

class Data_Handler_Weather(Data_Handler):
    """
    Sub data handler for the weather sensor.

    Any specific variables to this sensor will be
    defined in this sub-class.
    """

    def __init__(self,
                 variables=None,
                 variables_units=None,
                 **kwargs):

        self.variables = variables
        self.variables_units = variables_units

        super(Data_Handler_Weather, self).__init__(**kwargs)
