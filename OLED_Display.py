import ctypes
import datetime
import time
from dateutil import parser as theparser
import argparse
import sys
import signal
import numpy as np

sys.stdout.flush()

def proper_quit(*args):
    print("Exiting")
    OLED = OLED_Display()
    OLED.Pin_SetUp()
    ctypes.CDLL("/home/pi/oledtest/test.so").LCD_Init()
    print("Exiting")
    exit()

class OLED_Display:
    def _init_(self):
        pass

    returned_times = dict([("Air Quality Sensor", "0"), ("CO2 Sensor", "0"), ("Atmosphere Sensor", "0"), ("U.V. Sensor", "0"), ("Si Radiation Sensor", "0"), ("CsI Radiation Sensor", "0")])
    log_files = dict([("Air Quality Sensor", "air_quality_test_results.csv"), ("CO2 Sensor", "CO2_test_results.csv"), ("Atmosphere Sensor", "atmosphere_test_results.csv"), ("U.V. Sensor", "UV_test_results.csv"), ("Si Radiation Sensor", "si_rad_test_results.csv"), ("CsI Radiation Sensor", "csi_rad_test_results.csv")])

    #Selects certain columns to display from CSV files
    def display_which(self, sensor):
        if sensor == "Air Quality Sensor":
            display_which_column = [1,2,3,4,5,6,7,8,9]
        if sensor == "CO2 Sensor":
            display_which_column = [1]
        if sensor == "Atmosphere Sensor":
            display_which_column = [1, 2, 3]
        if sensor == "U.V. Sensor":
            display_which_column = [1]
        if sensor == "Si Radiation Sensor":
            display_which_column = [1]
        if sensor == "Csi Radiation Sensor":
            display_which_column = [1]

        return display_which_column

    #Sets up pins
    def Pin_SetUp(self):
        ctypes.CDLL("/usr/lib/libwiringPi.so").wiringPiSetup()
        ctypes.CDLL("/usr/lib/libwiringPi.so").pinMode(10, 1)
        ctypes.CDLL("/usr/lib/libwiringPi.so").pinMode(28, 1)
        ctypes.CDLL("/usr/lib/libwiringPi.so").pinMode(14, 1)
        ctypes.CDLL("/usr/lib/libwiringPi.so").pinMode(12, 1)
        ctypes.CDLL("/usr/lib/libwiringPi.so").pinMode(29, 1)

    #Checks if there is data in the log file
    def Check_Any(self, fname, sensor):
        try:
            check = open(fname).readlines()[0:2]
            while check == []:
                time.sleep(0.5)
                check = open(fname).readlines()[0:2]
                print(sensor+":")
                print("Error: Empty CSV \n")
                ctypes.CDLL("/home/pi/oledtest/test.so").LCD_Init()
                ctypes.CDLL("/home/pi/oledtest/test.so").LCD_P6x8Str(0,2,sensor+":")
                ctypes.CDLL("/home/pi/oledtest/test.so").LCD_P6x8Str(0,4,"Error: Empty CSV")
                time.sleep(2.5)
                ctypes.CDLL("/home/pi/oledtest/test.so").LCD_Init()
                return False
                break

            while len(check) < 2:
                time.sleep(0.5)
                check = open(fname).readlines()[0:2]
                print(sensor+":")
                print("Error: No Data \n")
                ctypes.CDLL("/home/pi/oledtest/test.so").LCD_Init()
                ctypes.CDLL("/home/pi/oledtest/test.so").LCD_P6x8Str(0,2,sensor+":")
                ctypes.CDLL("/home/pi/oledtest/test.so").LCD_P6x8Str(0,4,"Error: No Data")
                time.sleep(3)
                ctypes.CDLL("/home/pi/oledtest/test.so").LCD_Init()
                return False
                break

            return True

        except KeyboardInterrupt:
            proper_quit()

        except:
            print(sensor+":")
            print("Error Opening CSV \n")
            ctypes.CDLL("/home/pi/oledtest/test.so").LCD_Init()
            ctypes.CDLL("/home/pi/oledtest/test.so").LCD_P6x8Str(0,2,sensor+":")
            ctypes.CDLL("/home/pi/oledtest/test.so").LCD_P6x8Str(0,4,"Error Opening CSV")
            time.sleep(3)
            return False

    #Displays data on screen
    def Display_Data(self, fname, sensor):
        if self.Check_Any(self.log_files[sensor], sensor) == True:
            metadata_line = open(fname).readlines()[0:1]
            metadata = [line.split(",") for line in metadata_line]

            results = open(fname).readlines()[-1:]
            lastline = [line.split(",") for line in results]

            if "\n" in metadata[0][len(metadata[0])-1]:
                metadata[0][len(metadata[0])-1] = metadata[0][len(metadata[0])-1].strip("\n")

            if self.CheckIf_Repeat(lastline[0][0], sensor) == True:
                for i in self.display_which(sensor):
                    ctypes.CDLL("/home/pi/oledtest/test.so").LCD_Init()

                    if "\n" in lastline[0][i]:
                        lastline[0][i] = lastline[0][i].strip("\n")

                    to_be_displayed1 = str("Time       "+metadata[0][i])
                    to_be_displayed2 = str(theparser.parse(lastline[0][0]).strftime("%H:%M:%S")+"   "+lastline[0][i])

                    ctypes.CDLL("/home/pi/oledtest/test.so").LCD_P6x8Str(0,2,sensor+":") # x: until 100 and then starts again from y-axis; y: until 7
                    ctypes.CDLL("/home/pi/oledtest/test.so").LCD_P6x8Str(0,4,to_be_displayed1)
                    ctypes.CDLL("/home/pi/oledtest/test.so").LCD_P6x8Str(0,6,to_be_displayed2)
                    print(sensor+":")
                    print(to_be_displayed1)
                    print(to_be_displayed2+"\n")
                    time.sleep(3.5)

            elif self.CheckIf_Repeat(lastline[0][0], sensor) == False:
                print(sensor+":\nCouldn't Recieve Data \n")
                ctypes.CDLL("/home/pi/oledtest/test.so").LCD_Init()
                ctypes.CDLL("/home/pi/oledtest/test.so").LCD_P6x8Str(0,2,sensor+":")
                ctypes.CDLL("/home/pi/oledtest/test.so").LCD_P6x8Str(0,4,"Couldn't Recieve Data")
                time.sleep(3)

        else:
            pass

    #Checks if new data is being obtained
    def CheckIf_Repeat(self, returned_time, sensor):

        if self.returned_times[sensor] == returned_time:
            return False
        else:
            self.returned_times[sensor] = returned_time
            return True

signal.signal(signal.SIGINT, proper_quit)

try:
    time.sleep(3) #to give sensors time to start running
    try:
        OLED = OLED_Display()
        OLED.Pin_SetUp()
    except:
        print("Error Initializing")
        exit()

    sensor_name = []
    parser = argparse.ArgumentParser()
    parser.add_argument("-AQual", help = "Indicates inclusion of Air Quality Sensor", action = "store_true")
    parser.add_argument("-CO2", help = "Indicates inclusion of CO2 Sensor", action = "store_true")
    parser.add_argument("-Atmos", help = "Indicates inclusion of Atmosphere Sensor", action = "store_true")
    parser.add_argument("-UV", help = "Indicates inclusion of U.V. Sensor", action = "store_true")
    parser.add_argument("-Si", help = "Indicates inclusion of Si Radiation Sensor", action = "store_true")
    parser.add_argument("-CsI", help = "Indicates inclusion of CsI Radiation Sensor", action = "store_true")
    parser.add_argument("-Config", help = "Indicates usage of config.txt to determine list of sensors to run", action = "store_true")
    inclusion = parser.parse_args()

    AQ = inclusion.AQual
    CO = inclusion.CO2
    AT = inclusion.Atmos
    uv = inclusion.UV
    SI = inclusion.Si
    CSI = inclusion.CsI
    config = inclusion.Config

    if config == True:
        results = open("config.txt").readlines()
        for line in results:
            sensor_name = line.split(",")
        if "\n" in sensor_name[len(sensor_name)-1]:
            sensor_name[len(sensor_name)-1] = sensor_name[len(sensor_name)-1].strip("\n")

    else:
        if AQ == True:
            sensor_name.append("Air Quality Sensor")
        if CO == True:
            sensor_name.append("CO2 Sensor")
        if AT == True:
            sensor_name.append("Atmosphere Sensor")
        if uv == True:
            sensor_name.append("U.V. Sensor")
        if SI == True:
            sensor_name.append("Si Sensor")
        if CSI == True:
            sensor_name.append("CsI Sensor")
        if AQ == False and CO == False and AT == False and uv == False and SI == False and CSI == False:
            parser.print_help()
            exit()

        sensor_name = np.array(sensor_name)

    print("OLED Display Print: \n")

    while True:
        try:
            for i in range(len(sensor_name)):
                OLED.Display_Data(OLED.log_files[sensor_name[i]], sensor_name[i])

        except KeyboardInterrupt:
            proper_quit()

        except:
            print("Error: Exiting")
            ctypes.CDLL("/home/pi/oledtest/test.so").LCD_Init()
            ctypes.CDLL("/home/pi/oledtest/test.so").LCD_P6x8Str(0,3,"Error: Exiting")
            time.sleep(3)
            ctypes.CDLL("/home/pi/oledtest/test.so").LCD_Init()
            exit()

except:
    #proper_quit()
    pass
