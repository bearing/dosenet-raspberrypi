import ctypes
import datetime
import time
from dateutil import parser
import argparse

class OLED_Display:
    returned_times = dict([("Air Quality Sensor", 0), ("CO2 Sensor", 0), ("Atmosphere Sensor", 0), ("U.V. Sensor", 0), ("Si Radiation Sensor", 0), ("CsI Radiation Sensor", 0)])
    log_files = dict([("Air Quality Sensor", "air_quality_test_results.log"), ("CO2 Sensor", "CO2_test_results.log"), ("Atmosphere Sensor", "atmosphere_test_results.log"), ("U.V. Sensor", "UV_test_results.log"), ("Si Radiation Sensor", "si_rad_test_results.log"), ("CsI Radiation Sensor", "csi_rad_test_results.log")])
    #Opens General Result Files
    def Check_Any(a, fname, sensor):
        begin_time = int(time.time())
        check = open(fname).readlines()[0:2]
        while check == []:
            time.sleep(0.5)
            check = open(fname).readlines()[0:2]
            nowtime = int(time.time())
            if nowtime-begin_time > 3:
                ctypes.CDLL("/usr/lib/libwiringPi.so").wiringPiSetup()
                ctypes.CDLL("/usr/lib/libwiringPi.so").pinMode(10, 1)
                ctypes.CDLL("/usr/lib/libwiringPi.so").pinMode(5, 1)
                ctypes.CDLL("/usr/lib/libwiringPi.so").pinMode(14, 1)
                ctypes.CDLL("/usr/lib/libwiringPi.so").pinMode(12, 1)
                ctypes.CDLL("/usr/lib/libwiringPi.so").pinMode(6, 1)
                ctypes.CDLL("/home/pi/oledtest/test.so").LCD_Init()
                ctypes.CDLL("/home/pi/oledtest/test.so").LCD_P6x8Str(0,1,sensor)
                ctypes.CDLL("/home/pi/oledtest/test.so").LCD_P6x8Str(0,3,"Could Not Recieve Data")
                time.sleep(2)
                ctypes.CDLL("/home/pi/oledtest/test.so").LCD_Init()
                break

        begin_time = int(time.time())
        while len(check) < 2:
            time.sleep(0.5)
            check = open(fname).readlines()[0:2]
            nowtime = int(time.time())
            if nowtime-begin_time > 3:
                ctypes.CDLL("/usr/lib/libwiringPi.so").wiringPiSetup()
                ctypes.CDLL("/usr/lib/libwiringPi.so").pinMode(10, 1)
                ctypes.CDLL("/usr/lib/libwiringPi.so").pinMode(5, 1)
                ctypes.CDLL("/usr/lib/libwiringPi.so").pinMode(14, 1)
                ctypes.CDLL("/usr/lib/libwiringPi.so").pinMode(12, 1)
                ctypes.CDLL("/usr/lib/libwiringPi.so").pinMode(6, 1)
                ctypes.CDLL("/home/pi/oledtest/test.so").LCD_Init()
                ctypes.CDLL("/home/pi/oledtest/test.so").LCD_P6x8Str(0,1,sensor)
                ctypes.CDLL("/home/pi/oledtest/test.so").LCD_P6x8Str(0,3,"Could Not Recieve Data")
                time.sleep(2)
                ctypes.CDLL("/home/pi/oledtest/test.so").LCD_Init()
                break

    #Displays data on screen
    def Display_Data(a, fname, sensor):
        metadata_line = open(fname).readlines()[0:1]
        metadata = [line.split(",") for line in metadata_line]

        results = open(fname).readlines()[-1:]
        lastline = [line.split(",") for line in results]
        ctypes.CDLL("/usr/lib/libwiringPi.so").wiringPiSetup()
        ctypes.CDLL("/usr/lib/libwiringPi.so").pinMode(10, 1)
        ctypes.CDLL("/usr/lib/libwiringPi.so").pinMode(5, 1)
        ctypes.CDLL("/usr/lib/libwiringPi.so").pinMode(14, 1)
        ctypes.CDLL("/usr/lib/libwiringPi.so").pinMode(12, 1)
        ctypes.CDLL("/usr/lib/libwiringPi.so").pinMode(6, 1)

        for i in range(1,len(lastline[0])):
            ctypes.CDLL("/home/pi/oledtest/test.so").LCD_Init()
            if "\n" in metadata[0][i]:
                metadata[0][i] = metadata[0][i].strip("\n")
            if "\n" in lastline[0][i]:
                lastline[0][i] = lastline[0][i].strip("\n")
            to_be_displayed1 = str("Time       "+metadata[0][i])
            to_be_displayed2 = str(parser.parse(lastline[0][0]).strftime("%H:%M:%S")+"   "+lastline[0][i])
            ctypes.CDLL("/home/pi/oledtest/test.so").LCD_P6x8Str(0,2,sensor) # x: until 100 and then starts again from y-axis; y: until 7
            ctypes.CDLL("/home/pi/oledtest/test.so").LCD_P6x8Str(0,4,to_be_displayed1)
            ctypes.CDLL("/home/pi/oledtest/test.so").LCD_P6x8Str(0,6,to_be_displayed2)
        return time.mktime(t.timetuple(metadata[0][0]))

    def CheckIf_Repeat(a, returned_time, sensor):
        if self.returned_times[sensor] == returned_time:
            ctypes.CDLL("/usr/lib/libwiringPi.so").wiringPiSetup()
            ctypes.CDLL("/usr/lib/libwiringPi.so").pinMode(10, 1)
            ctypes.CDLL("/usr/lib/libwiringPi.so").pinMode(5, 1)
            ctypes.CDLL("/usr/lib/libwiringPi.so").pinMode(14, 1)
            ctypes.CDLL("/usr/lib/libwiringPi.so").pinMode(12, 1)
            ctypes.CDLL("/usr/lib/libwiringPi.so").pinMode(6, 1)
            ctypes.CDLL("/home/pi/oledtest/test.so").LCD_Init()
            ctypes.CDLL("/home/pi/oledtest/test.so").LCD_P6x8Str(0,2,sensor)
            ctypes.CDLL("/home/pi/oledtest/test.so").LCD_P6x8Str(0,4,"Could Not Recieve Data")

        else:
            self.returned_times[sensor] = returned_time

sensor_name = []
parser = argparse.ArgumentParser()
inclusion = parser.parse_args()

parser.add_argument("-AQual", help = "Indicates inclusion of Air Quality Sensor.", action = "store_false")
parser.add_argument("-CO2", help = "Indicates inclusion of CO2 Sensor.", action = "store_false")
parser.add_argument("-Atmos", help = "Indicates inclusion of Atmosphere Sensor.", action = "store_false")
parser.add_argument("-UV", help = "Indicates inclusion of U.V. Sensor.", action = "store_false")
parser.add_argument("-Si", help = "Indicates inclusion of Si Radiation Sensor.", action = "store_false")
parser.add_argument("-CsI", help = "Indicates inclusion of CsI Radiation Sensor.", action = "store_false")

AQ = inclusion.-AQual
CO = inclusion.-CO2
AT = inclusion.-Atmos
uv = inclusion.-UV
SI = inclusion.-Si
CSI = inclusion.-CsI

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
    for i in range(len(sensor_name)):
        OLED = OLED_Display()
        OLED.Check_Any(log_files[sensor_name[i]], sensor_name[i])

    while True:
        for i in range(len(sensor_name)):
            OLED.CheckIf_Repeat(OLED.Display_Data(log_files[sensor_name[i]], sensor_name[i]), sensor_name[i])
            time.sleep(3.5)

except:
    ctypes.CDLL("/usr/lib/libwiringPi.so").wiringPiSetup()
    ctypes.CDLL("/usr/lib/libwiringPi.so").pinMode(10, 1)
    ctypes.CDLL("/usr/lib/libwiringPi.so").pinMode(5, 1)
    ctypes.CDLL("/usr/lib/libwiringPi.so").pinMode(14, 1)
    ctypes.CDLL("/usr/lib/libwiringPi.so").pinMode(12, 1)
    ctypes.CDLL("/usr/lib/libwiringPi.so").pinMode(6, 1)
    ctypes.CDLL("/home/pi/oledtest/test.so").LCD_Init()
    ctypes.CDLL("/home/pi/oledtest/test.so").LCD_P6x8Str(0,3,"Error: Exiting")
    ctypes.CDLL("/home/pi/oledtest/test.so").LCD_Init()
    exit()
