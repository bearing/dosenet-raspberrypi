import ctypes

ctypes.CDLL("/usr/lib/libwiringPi.so").wiringPiSetup()
ctypes.CDLL("/usr/lib/libwiringPi.so").pinMode(10, 1)
ctypes.CDLL("/usr/lib/libwiringPi.so").pinMode(5, 1)
ctypes.CDLL("/usr/lib/libwiringPi.so").pinMode(14, 1)
ctypes.CDLL("/usr/lib/libwiringPi.so").pinMode(12, 1)
ctypes.CDLL("/usr/lib/libwiringPi.so").pinMode(6, 1)
ctypes.CDLL("/home/pi/oledtest/test.so").LCD_Init()
ctypes.CDLL("/home/pi/oledtest/test.so").LCD_P6x8Str(50,4,"Works") # x: until 100 and then starts again from y-axis, y: until 6

