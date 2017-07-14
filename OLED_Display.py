import ctypes
import datetime
import time
from dateutil import parser

constant_count = 0
counter = 0
time_store = ""

check_any = open("air_quality_test_results.log").readlines()[0:2]

while check_any == []:
    time.sleep(0.5)
    check_any = open("air_quality_test_results.log").readlines()[0:2]
print len(check_any)
while len(check_any) < 2:
    time.sleep(0.5)
    check_any = open("air_quality_test_results.log").readlines()[0:2]

for i in open("air_quality_test_results.log"):
    counter += 1

metadata_line = open("air_quality_test_results.log").readlines()[0:1]
metadata = [line.split(",") for line in metadata_line]

while constant_count <= counter:
    constant_count = counter
    results = open("air_quality_test_results.log").readlines()[-1:]
    lastline = [line.split(",") for line in results]
    ctypes.CDLL("/usr/lib/libwiringPi.so").wiringPiSetup()
    ctypes.CDLL("/usr/lib/libwiringPi.so").pinMode(10, 1)
    ctypes.CDLL("/usr/lib/libwiringPi.so").pinMode(5, 1)
    ctypes.CDLL("/usr/lib/libwiringPi.so").pinMode(14, 1)
    ctypes.CDLL("/usr/lib/libwiringPi.so").pinMode(12, 1)
    ctypes.CDLL("/usr/lib/libwiringPi.so").pinMode(6, 1)
    ctypes.CDLL("/home/pi/oledtest/test.so").LCD_Init()

    for i in range(1,len(lastline[0])):
        if "\n" in metadata[0][i]:
            metadata[0][i] = metadata[0][i].strip("\n")
        if "\n" in lastline[0][i]:
            lastline[0][i] = lastline[0][i].strip("\n")
        to_be_displayed1 = str("Time:      "+metadata[0][i]+":")
        to_be_displayed2 = str(parser.parse(lastline[0][0]).strftime("%H:%M:%S")+"   "+lastline[0][i])
        if time_store == parser.parse(lastline[0][0]).strftime("%H:%M:%S") and metadata[0][i] == "0.3 um":
            ctypes.CDLL("/home/pi/oledtest/test.so").LCD_Init()
            exit()
        print(to_be_displayed1)
        print(to_be_displayed2)
        ctypes.CDLL("/home/pi/oledtest/test.so").LCD_P6x8Str(0,2,to_be_displayed1) # x: until 100 and then starts again from y-axis; y: until 7
        ctypes.CDLL("/home/pi/oledtest/test.so").LCD_P6x8Str(0,4,to_be_displayed2)
        time.sleep(3)
        time_store = parser.parse(lastline[0][0]).strftime("%H:%M:%S")

    counter = 0
    for i in open("air_quality_test_results.log"):
        counter += 1
