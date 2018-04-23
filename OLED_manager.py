import ctypes
import datetime
import time
import argparse
import sys

class OLED_Manager(object):
    """
    OLED display manager class to control the OLED display and
    display data straight from the different types of sensors (hopefully)
    """
    def __init__(self,
                 sensor_type=None,
                 wait_time=None):

        self.sensor_type = sensor_type
        self.wait_time = wait_time

        self.OLED_Pin_Setup()

    def OLED_Pin_Setup(self):
        """
        This function sets up the pins for the OLED screen and
        displays a small message when complete
        """
        ctypes.CDLL("/usr/lib/libwiringPi.so").wiringPiSetup()
        types.CDLL("/usr/lib/libwiringPi.so").pinMode(10, 1)
        types.CDLL("/usr/lib/libwiringPi.so").pinMode(28, 1)
        types.CDLL("/usr/lib/libwiringPi.so").pinMode(14, 1)
        types.CDLL("/usr/lib/libwiringPi.so").pinMode(12, 1)
        types.CDLL("/usr/lib/libwiringPi.so").pinMode(29, 1)

        ctypes.CDLL("/home/pi/oledtest/test.so").LCD_Init()
        ctypes.CDLL("/home/pi/oledtest/test.so").LCD_P6x8Str(15, 3, "Pin Setup Complete!")
        print("Pin Setup Complete!")
        time.sleep(1.5)
        ctypes.CDLL("/home/pi/oledtest/test.so").LCD_Init()

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
                ctypes.CDLL("/home/pi/oledtest/test.so").LCD_Init()
        else:
            print("Trying to display something that wasn't a string! Try making it a string.")

    def oclear(self):
        """
        This function is meant to shorten the code needed to clear the
        OLED screen.
        """
        ctypes.CDLL("/home/pi/oledtest/test.so").LCD_Init()

    def Read_Data(self, file, sensor):
        """
        This function is meant to read data from a CSV file and 
