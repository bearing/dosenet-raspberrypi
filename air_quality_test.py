import serial

print('Running Test Script')
port = serial.Serial("/dev/ttyAMA0", baudrate=9600, timeout=1500)

while True: 
  recv = port.read(10)
  print(recv)
