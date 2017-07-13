import ctypes
import datetime

constant_count = 0
for i in open("air_quality_test_results_2017-06-29_17-33-06.csv"):
        counter += 1

while constant_count <= counter:
    constant_count = counter
    results = open("air_quality_test_results_2017-06-29_17-33-06.csv").readlines()[-1:]
    lastline = [line.split(",") for line in results]

    ctypes.CDLL("/usr/lib/libwiringPi.so").wiringPiSetup()
    ctypes.CDLL("/usr/lib/libwiringPi.so").pinMode(10, 1)
    ctypes.CDLL("/usr/lib/libwiringPi.so").pinMode(5, 1)
    ctypes.CDLL("/usr/lib/libwiringPi.so").pinMode(14, 1)
    ctypes.CDLL("/usr/lib/libwiringPi.so").pinMode(12, 1)
    ctypes.CDLL("/usr/lib/libwiringPi.so").pinMode(6, 1)
    ctypes.CDLL("/home/pi/oledtest/test.so").LCD_Init()

    for i in range(1,len(lastline)+2):
        to_be_displayed = str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")+" "+lastline[i])
        ctypes.CDLL("/home/pi/oledtest/test.so").LCD_P6x8Str(50,4,to_be_displayed) # x: until 100 and then starts again from y-axis, y: until 6

    counter = 0

    for i in open("air_quality_test_results_2017-06-29_17-33-06.csv"):
        counter += 1