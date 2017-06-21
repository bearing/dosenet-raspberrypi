
import serial
import ast
import binascii

print('Running Test Script')
port = serial.Serial("/dev/ttyS0", baudrate=9600, timeout=1.5)
while True: 
    print('next')
    text = port.read(32)
    #print(text)
    buffer = [ord(c) for c in text]
    if buffer[0] == 66:
        print(buffer)
        #print(len(buffer))
        #Check sum with last byte of list 
        sumation = sum(buffer[0:30])
        checkbyte = (buffer[30]<<8)+buffer[31]
        print(sumation)
        print(checkbyte)
        if sumation == ((buffer[30]<<8)+buffer[31]):
            #print('Sum check complete')
            buf = buffer[1:32]

            # Get concentrations ug/m3
            PM01Val=((buf[3]<<8) + buf[4])
            PM25Val=((buf[5]<<8) + buf[6])
            PM10Val=((buf[7]<<8) + buf[8])

            # Get number of particles in 0.1 L of air above specific diameters


            P3  =((buf[15]<<8) + buf[16])
            P5  =((buf[17]<<8) + buf[18])
            P10 =((buf[19]<<8) + buf[20])
            P25 =((buf[21]<<8) + buf[22])
            P50 =((buf[23]<<8) + buf[24])
            P100=((buf[25]<<8) + buf[26])

            # Print Concentrations [ug/m3]
            print('\nConcentration of Particulate Matter [ug/m3]\n')
            print('PM 1.0 = ' + repr(PM01Val) +' ug/m3')
            print('PM 2.5 = ' + repr(PM25Val) +' ug/m3')
            print('PM 10  = ' + repr(PM10Val) +' ug/m3\n')

            # Print number of particles in 0.1 L of air over specific diamaters
            print('Number of particles in 0.1 L of air with specific diameter\n')
            print('#Particles, diameter over 0.3 um = ' + repr(P3))
            print('#Particles, diameter over 0.5 um = ' + repr(P5))
            print('#Particles, diameter over 1.0 um = ' + repr(P10))
            print('#Particles, diameter over 2.5 um = ' + repr(P25))
            print('#Particles, diameter over 5.0 um = ' + repr(P50))
            print('#Particles, diameter over 10  um = ' + repr(P100))

        else:
            print('Check Sum Failed')
