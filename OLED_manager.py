import ctypes
import datetime
import time
import argparse
import sys
import os
import pika
import json

class OLED_Manager(object):
    """
    OLED display manager class to control the OLED display and
    display data straight from the different types of sensors (hopefully)
    """
    def __init__(self,
                 sensor_type=None,
                 display_time=None,
                 data_file=None):

        self.sensor_type = sensor_type
        self.display_time = display_time

        self.data_file = data_file

        self.OLED_Pin_Setup()

        self.sdisp_names = ["Pocket Geiger Counter", "D3S", "Air Quality Sensor", "CO2 Sensor", "Weather Sensor"]
        self.dispcol = [0,54,9,33,21]
        #In form of: "at HH:MM:SSAM"
        self.time_dispcol = [24]
        #In form of: "Data received from:"
        self.basic_dispcol = [6]

        #self.receiver_setup()

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

    def receiver_setup(self):
        """
        This function sets up this manager as a consumer on the
        rabbitmq queue chain
        """
        connection = pika.BlockingConnection(
            pika.ConnectionParameters(host='localhost')
        )
        channel = connection.channel()

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

    def run():
        """
        Runs the OLED as a consumer and displays data as it receives it
        """
