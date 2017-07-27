import ctypes
import datetime
import time
from dateutil import parser as theparser
import argparse
import sys

sys.stdout.flush()

class OLED_Display:
    def _init_(self):
        pass

    returned_times = dict([("Air Quality Sensor", "0"), ("CO2 Sensor", "0"), ("Atmosphere Sensor", "0"), ("U.V. Sensor", "0"), ("Si Radiation Sensor", "0"), ("CsI Radiation Sensor", "0")])
    log_files = dict([("Air Quality Sensor", "air_quality_test_results.csv"), ("CO2 Sensor", "CO2_test_results.csv"), ("Atmosphere Sensor", "atmosphere_test_results.csv"), ("U.V. Sensor", "UV_test_results.csv"), ("Si Radiation Sensor", "si_rad_test_results.csv"), ("CsI Radiation Sensor", "csi_rad_test_results.csv")])

    #Sets up pins
    def Pin_SetUp(self):
        ctypes.CDLL("/usr/lib/libwiringPi.so").wiringPiSetup()
        ctypes.CDLL("/usr/lib/libwiringPi.so").pinMode(10, 1)
        ctypes.CDLL("/usr/lib/libwiringPi.so").pinMode(28, 1)
        ctypes.CDLL("/usr/lib/libwiringPi.so").pinMode(14, 1)
        ctypes.CDLL("/usr/lib/libwiringPi.so").pinMode(12, 1)
        ctypes.CDLL("/usr/lib/libwiringPi.so").pinMode(29, 1)

    #Opens General Result Files
    def Check_Any(self, fname, sensor):
        begin_time = int(time.time())
        check = open(fname).readlines()[0:2]
        while check == []:
            time.sleep(0.5)
            check = open(fname).readlines()[0:2]
            nowtime = int(time.time())
            if nowtime-begin_time > 3:
                ctypes.CDLL("/home/pi/oledtest/test.so").LCD_Init()
                ctypes.CDLL("/home/pi/oledtest/test.so").LCD_P6x8Str(0,1,sensor)
                time.sleep(2)
                ctypes.CDLL("/home/pi/oledtest/test.so").LCD_Init()
                break

        begin_time = int(time.time())
        while len(check) < 2:
            time.sleep(0.5)
            check = open(fname).readlines()[0:2]
            nowtime = int(time.time())
            if nowtime-begin_time > 3:
                ctypes.CDLL("/home/pi/oledtest/test.so").LCD_Init()
                ctypes.CDLL("/home/pi/oledtest/test.so").LCD_P6x8Str(0,1,sensor)
                ctypes.CDLL("/home/pi/oledtest/test.so").LCD_P6x8Str(0,3,"Couldn't Recieve Data")
                time.sleep(2)
                ctypes.CDLL("/home/pi/oledtest/test.so").LCD_Init()
                break

    #Displays data on screen
    def Display_Data(self, fname, sensor):
        metadata_line = open(fname).readlines()[0:1]
        metadata = [line.split(",") for line in metadata_line]

        results = open(fname).readlines()[-1:]
        lastline = [line.split(",") for line in results]
        print len(metadata)
        print len(metadata[0])

        if "\n" in metadata[0][len(metadata[0])]:
            metadata[0][len(metadata[0])] = metadata[0][len(metadata[0])].strip("\n")
            print "test"
        
        if self.CheckIf_Repeat(lastline[0][0], sensor) == True:
            for i in range(1,len(lastline[0])):
                ctypes.CDLL("/home/pi/oledtest/test.so").LCD_Init()

                if "\n" in lastline[0][i]:
                    lastline[0][i] = lastline[0][i].strip("\n")

                to_be_displayed1 = str("Time       "+metadata[0][i])
                to_be_displayed2 = str(theparser.parse(lastline[0][0]).strftime("%H:%M:%S")+"   "+lastline[0][i])

                ctypes.CDLL("/home/pi/oledtest/test.so").LCD_P6x8Str(0,2,sensor+":") # x: until 100 and then starts again from y-axis; y: until 7
                ctypes.CDLL("/home/pi/oledtest/test.so").LCD_P6x8Str(0,4,to_be_displayed1)
                ctypes.CDLL("/home/pi/oledtest/test.so").LCD_P6x8Str(0,6,to_be_displayed2)
                print(to_be_displayed1)
                print(to_be_displayed2)
                time.sleep(3.5)

        elif self.CheckIf_Repeat(lastline[0][0], sensor) == False:
            ctypes.CDLL("/home/pi/oledtest/test.so").LCD_Init()
            ctypes.CDLL("/home/pi/oledtest/test.so").LCD_P6x8Str(0,2,sensor)
            ctypes.CDLL("/home/pi/oledtest/test.so").LCD_P6x8Str(0,4,"Couldn't Recieve Data")
            time.sleep(3)

    def CheckIf_Repeat(self, returned_time, sensor):
        if self.returned_times[sensor] == returned_time:
            return False

        else:
            self.returned_times[sensor] = returned_time
            return True

sensor_name = []
parser = argparse.ArgumentParser()
parser.add_argument("-AQual", help = "Indicates inclusion of Air Quality Sensor.", action = "store_true")
parser.add_argument("-CO2", help = "Indicates inclusion of CO2 Sensor.", action = "store_true")
parser.add_argument("-Atmos", help = "Indicates inclusion of Atmosphere Sensor.", action = "store_true")
parser.add_argument("-UV", help = "Indicates inclusion of U.V. Sensor.", action = "store_true")
parser.add_argument("-Si", help = "Indicates inclusion of Si Radiation Sensor.", action = "store_true")
parser.add_argument("-CsI", help = "Indicates inclusion of CsI Radiation Sensor.", action = "store_true")
inclusion = parser.parse_args()

AQ = inclusion.AQual
CO = inclusion.CO2
AT = inclusion.Atmos
uv = inclusion.UV
SI = inclusion.Si
CSI = inclusion.CsI

if AQ == True:
    sensor_name.append("Air Quality Sensor")
elif CO == True:
    sensor_name.append("CO2 Sensor")
elif AT == True:
    sensor_name.append("Atmosphere Sensor")
elif uv == True:
    sensor_name.append("U.V. Sensor")
elif SI == True:
    sensor_name.append("Si Sensor")
elif CSI == True:
    sensor_name.append("CsI Sensor")
else:
    parser.print_help()
    exit()

try:
    OLED = OLED_Display()
    OLED.Pin_SetUp()
    for i in range(len(sensor_name)):
        OLED.Check_Any(OLED.log_files[sensor_name[i]], sensor_name[i])
    while True:
        for i in range(len(sensor_name)):
            OLED.Display_Data(OLED.log_files[sensor_name[i]], sensor_name[i])

except:
    ctypes.CDLL("/usr/lib/libwiringPi.so").wiringPiSetup()
    ctypes.CDLL("/usr/lib/libwiringPi.so").pinMode(10, 1)
    ctypes.CDLL("/usr/lib/libwiringPi.so").pinMode(28, 1)
    ctypes.CDLL("/usr/lib/libwiringPi.so").pinMode(14, 1)
    ctypes.CDLL("/usr/lib/libwiringPi.so").pinMode(12, 1)
    ctypes.CDLL("/usr/lib/libwiringPi.so").pinMode(29, 1)
    ctypes.CDLL("/home/pi/oledtest/test.so").LCD_Init()
    ctypes.CDLL("/home/pi/oledtest/test.so").LCD_P6x8Str(0,3,"Error: Exiting")
    time.sleep(3.5)
    ctypes.CDLL("/home/pi/oledtest/test.so").LCD_Init()
    exit()
