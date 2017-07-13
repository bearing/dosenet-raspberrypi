import ctypes
import datetime
import time

constant_count = 0
counter = 0

for i in open("air_quality_test_results.csv"):
    counter += 1

metadata_line = open("air_quality_test_results.csv").readlines()[0:1]
metadata = [line.split(",") for line in metadata_line]

while constant_count <= counter:
    constant_count = counter
    results = open("air_quality_test_results.csv").readlines()[-1:]
    lastline = [line.split(",") for line in results]

    ctypes.CDLL("/usr/lib/libwiringPi.so").wiringPiSetup()
    ctypes.CDLL("/usr/lib/libwiringPi.so").pinMode(10, 1)
    ctypes.CDLL("/usr/lib/libwiringPi.so").pinMode(5, 1)
    ctypes.CDLL("/usr/lib/libwiringPi.so").pinMode(14, 1)
    ctypes.CDLL("/usr/lib/libwiringPi.so").pinMode(12, 1)
    ctypes.CDLL("/usr/lib/libwiringPi.so").pinMode(6, 1)
    ctypes.CDLL("/home/pi/oledtest/test.so").LCD_Init()

    while len(lastline[0]) > 0:
        for i in range(1,len(lastline[0])):
            to_be_displayed1 = str("Time:      "+metadata[0][i]+" Value")
            to_be_displayed2 = str(datetime.datetime.now().strftime("%H:%M:%S")+"   "+lastline[0][i])
            ctypes.CDLL("/home/pi/oledtest/test.so").LCD_P6x8Str(0,2,to_be_displayed1) # x: until 100 and then starts again from y-axis; y: until 7
            ctypes.CDLL("/home/pi/oledtest/test.so").LCD_P6x8Str(0,4,to_be_displayed2)
            time.sleep(3)

    counter = 0
    for i in open("air_quality_test_results.csv"):
        counter += 1
