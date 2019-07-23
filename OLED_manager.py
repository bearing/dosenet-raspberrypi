import ctypes
import datetime
import time
import math
import argparse
import sys
import os
import pika
import json
import random

from auxiliaries import set_verbosity
from globalvalues import DEFAULT_LOGFILE_OLED, DEFAULT_DISPLAY_TIME_OLED

class OLED_Manager(object):
    """
    OLED display manager class to control the OLED display and
    display data straight from the different types of sensors (hopefully)
    """
    def __init__(self,
                 display_time=None,
                 logfile=None,
                 verbosity=None,
                 test=None):

        self.logfile = logfile

        self.test = test

        if self.test:
            if display_time is None:
                display_time = DEFAULT_DISPLAY_TIME_OLED

        if verbosity is None:
            if self.test:
                verbosity = 3
            else:
                verbosity = 1
        self.v = verbosity

        set_verbosity(self)

        self.OLED_Pin_Setup()

        self.disp_names = ("Data received from:", "at ", "Pocket Geiger Counter",
            "D3S", "Air Quality Sensor", "CO2 Sensor", "Weather Sensor", "Unknown Sensor :(")
        #In the form of: [Data, Time, PG, D3S, AQS, CO2S, WS, US]
        self.disp_col = (6,24,0,54,9,33,21,12)

        self.rad_disp = ("CPM: ", "Dose Rate:", "uSv/hr")
        self.aq_disp = ("PM2.5: ", "PM10: ")
        self.co2_disp = ("CO2 Concentration:", "ppm")
        self.weather_disp = ("Pressure: ", "hPa", "Temperature: ", "C", "Humidity: ", "%")

    def create_test_data(self, sensor):
        """
        Generates a pseudo-random set of data based on which sensor is called.

        Note: the pseudo-random seed for this computation is set based on the time of the
        callback which helps ensure more randomness
        """
        random.seed(time.time())
        if sensor == 1:
            data = [random.randint(1,400), random.randint(1,20)]
        elif sensor == 2:
            data = [random.randint(1000,1800000)/float(random.randint(30,300))]
        elif sensor == 3:
            data = [round(random.uniform(0,6),2), round(random.uniform(0,6),2), round(random.uniform(0,5),2),
                round(random.uniform(0,1000),2), round(random.uniform(0,500),2), round(random.uniform(0,150),2),
                round(random.uniform(0,5),2), round(random.uniform(0,2),2), round(random.uniform(0,2),2)]
        elif sensor == 4:
            data = [round(random.uniform(300,900),2), round(random.uniform(0,3),2)]
        elif sensor == 5:
            data = [round(random.uniform(0,30),2), round(random.uniform(800,1200),2), round(random.uniform(0,100),2)]
        else:
            data = None
        return data

    def OLED_Pin_Setup(self):
        """
        This function sets up the pins for the OLED screen and
        displays a small message when complete
        """
        ctypes.CDLL("/usr/lib/libwiringPi.so").wiringPiSetup()
        ctypes.CDLL("/usr/lib/libwiringPi.so").pinMode(10, 1)
        ctypes.CDLL("/usr/lib/libwiringPi.so").pinMode(28, 1)
        ctypes.CDLL("/usr/lib/libwiringPi.so").pinMode(14, 1)
        ctypes.CDLL("/usr/lib/libwiringPi.so").pinMode(12, 1)
        ctypes.CDLL("/usr/lib/libwiringPi.so").pinMode(29, 1)

        ctypes.CDLL("/home/pi/oledtest/test.so").LCD_Init()
        ctypes.CDLL("/home/pi/oledtest/test.so").LCD_P6x8Str(6, 3, "Pin Setup Complete!")
        print("Pin Setup Complete!")
        time.sleep(1.5)
        ctypes.CDLL("/home/pi/oledtest/test.so").LCD_Fill(0x00)

    def oprint(self, x, y, print_text, display_time=None):
        """
        This function is meant to shorten the code needed to print to
        the OLED screen. If a display_time is entered, it will display
        the message for that many seconds and then clear the screen.
        """
        if isinstance(print_text, str):
            ctypes.CDLL("/home/pi/oledtest/test.so").LCD_P6x8Str(x, y, print_text)
            if display_time:
                time.sleep(display_time)
                ctypes.CDLL("/home/pi/oledtest/test.so").LCD_Fill(0x00)
        else:
            print("Trying to display something that wasn't a string! Try making it a string.")

    def oclear(self):
        """
        This function is meant to shorten the code needed to clear the
        OLED screen.
        """
        ctypes.CDLL("/home/pi/oledtest/test.so").LCD_Fill(0x00)

    def det_col(disp_str):
        """
        This function calculates the optimal starting pixel to
        center the display text on the OLED screen.
        """
        disp_col = int(math.floor(3*(21-len(disp_str))))
        return disp_col

    def display_data(sid, data):
        """
        This function uses the sensor type to determine how to
        display given data then prints it to the OLED screen.

        Currently can handle:
        Pocket Geiger, D3S, Air Quality Sensor, CO2 Sensor, Weather Sensor
        and any Unknown Sensor
        """
        self.oprint(self.disp_col[0], 0, self.disp_names[0])
        timestr = self.disp_names[1] + datetime.datetime.now().strftime('%I:%M:%S%p')
        self.oprint(self.disp_col[1], 2, timestr)
        self.oprint(0,3,'---------------------')

        if sid == 1:
            cpm, cpm_err = data[0], round(data[1],2)
            doserate = cpm*0.0357
            cpm_disp = self.rad_disp[0]+str(cpm)
            doserate_data_disp = str(round(doserate,3))+self.rad_disp[2]
            self.oprint(self.disp_col[sid+1], 1, self.disp_names[sid+1])
            self.oprint(self.det_col(cpm_disp), 4, cpm_disp)
            self.oprint(33, 5, self.rad_disp[1])
            self.oprint(self.det_col(doserate_data_disp), 6, doserate_data_disp)
        elif sid == 2:
            cps = data[0]
            doserate, cpm = cps*60*0.0000427, cps*60
            cpm_disp = self.rad_disp[0]+str(cpm)
            doserate_data_disp = str(round(doserate,3))+self.rad_disp[2]
            self.oprint(self.disp_col[sid+1], 1, self.disp_names[sid+1])
            self.oprint(self.det_col(cpm_disp), 4, cpm_disp)
            self.oprint(33, 5, self.rad_disp[1])
            self.oprint(self.det_col(doserate_data_disp), 6, doserate_data_disp)
        elif sid == 3:
            PM1, PM25, PM10 = data[0], data[1], data[2]
            U03, U05, U1, U25, U5, U10 = data[3], data[4], data[5], data[6], data[7], data[8]
            PM25_disp, PM10_disp = self.aq_disp[0]+str(PM25), self.aq_disp[1]+str(PM10)
            self.oprint(self.disp_col[sid+1], 1, self.disp_names[sid+1])
            self.oprint(self.det_col(PM25_disp), 4, PM25_disp)
            self.oprint(self.det_col(PM10_disp), 5, PM10_disp)
        elif sid == 4:
            conc, uv = data[0], data[1]
            conc_data_disp = str(conc)+self.co2_disp[1]
            self.oprint(self.disp_col[sid+1], 1, self.disp_names[sid+1])
            self.oprint(9, 4, self.co2_disp[0])
            self.oprint(self.det_col(conc_data_disp), 5, conc_data_disp)
        elif sid == 5:
            temp, pres, humid = data[0], data[1], data[2]
            pres_disp = self.weather_disp[0]+str(pres)+self.weather_disp[1]
            temp_disp = self.weather_disp[2]+str(temp)+self.weather_disp[3]
            humid_disp = self.weather_disp[4]+str(humid)+self.weather_disp[5]
            self.oprint(self.disp_col[sid+1], 1, self.disp_names[sid+1])
            self.oprint(self.det_col(pres_disp), 4, pres_disp)
            self.oprint(self.det_col(temp_disp), 5, temp_disp)
            self.oprint(self.det_col(humid_disp), 6, humid_disp)
        else:
            self.oprint(self.disp_col[7], 1, self.disp_names[7])

    def callback(channel, method_frame, header_frame, body):
        """
        This function automatically runs whenever the running consumer
        instance receives a data packet.
        """
        self.vprint(
            1, "Received data at: {}".format(datetime.datetime.now().strftime("%H:%M:%S")))
        data = json.loads(body)
        self.vprint(2, "The id is: {}".format(data['id']))
        self.vprint(2, "The data is: {}".format(data['data']))
        self.display_data(data['id'],data['data'])
        time.sleep(self.display_time)
        self.oclear()

    def run():
        """
        Runs the OLED as a consumer and displays data as it receives it.
        """
        if not self.test:
            connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
            channel = connection.channel()
            channel.queue_declare(queue='toOLED')

            channel.basic_consume(queue='toOLED', on_message_callback=self.callback, auto_ack=True)

            self.vprint(1, "Now waiting for data from sensors.")
            channel.start_consuming()
        else:
            self.display_time = 30
            for sensor in range(0,5):
                self.vprint(1, "Now creating random data for the "+self.disp_names[sensor+2])
                data = {'id': sensor, 'data': create_test_data(sensor)}
                self.vprint(1, "The randomized data is: "+str(data['data']))
                self.callback(None, None, None, data)
            self.vprint(1, "Testing complete, make sure all data was displayed properly.")

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--display_time', '-d', type=int, help=('Enter a number corresponding '+
        'to the amount of time that data \nfrom each sensor will display on '+
        'the OLED screen (default {})').format(DEFAULT_DISPLAY_TIME_OLED))
    parser.add_argument(
        '--logfile', '-l', type=str, default=None,
        help='Specify the path of the file for logging (default {})'.format(DEFAULT_LOGFILE_OLED))
    parser.add_argument(
        '--verbosity', '-v', type=int, default=None,
        help='Verbosity level (0 to 3) (default 1)')
    parser.add_argument(
        '--test', '-t', action='store_true', default=False,
        help='Turns testing mode on (setting other things along with that)')

    args = parser.parse_args()
    arg_dict = vars(args)

    mgr = OLED_Manager(**arg_dict)

    try:
        mgr.run()
    except:
        if mgr.logfile:
            # print exception info to logfile
            with open(mgr.logfile, 'a') as f:
                traceback.print_exc(15, f)
        # regardless, re-raise the error which will print to stderr
        raise
