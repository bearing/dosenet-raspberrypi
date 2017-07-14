import ctypes
import datetime
import time

constant_count = 0
counter = 0

for i in open("air_quality_test_results.csv"):
    counter += 1

metadata_line = open("air_quality_test_results.csv").readlines()[0:1]
metadata = [line.split(",") for line in metadata_line]

check_any = open("air_quality_test_results.csv").readlines()[0:2]

print check_any

while check_any == []:
    time.sleep(2)
    check_any = open("air_quality_test_results.csv").readlines()[0:2]

print check_any

while len(check_any) < 2:
    time.sleep(2)
    check_any = open("air_quality_test_results.csv").readlines()[0:2]

print check_any

print metadata[0]
print metadata[0][1]

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
            print metadata[0][i]
            if "/n" in metadata[0][i]:
                metadata_final = [metadata[0][i].split()]
                metadata_final.pop()
                metadata_final.pop()
            if "/n" in lastline[0][i]:
                lastline_final = [lastline[0][i].split()]
                lastline_final.pop()
                lastline_final.pop()
            to_be_displayed1 = str("Time:      "+metadata[0][i]+":")
            to_be_displayed2 = str(datetime.datetime.now().strftime("%H:%M:%S")+"   "+lastline[0][i])
            print(to_be_displayed1)
            print(to_be_displayed2)
            ctypes.CDLL("/home/pi/oledtest/test.so").LCD_P6x8Str(0,2,to_be_displayed1) # x: until 100 and then starts again from y-axis; y: until 7
            ctypes.CDLL("/home/pi/oledtest/test.so").LCD_P6x8Str(0,4,to_be_displayed2)
            time.sleep(3)

    counter = 0
    for i in open("air_quality_test_results.csv"):
        counter += 1
