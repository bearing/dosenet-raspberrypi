
import serial
import ast
import binascii
import csv
import datetime

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

            # Put results in a CSV file
            results = []
            pen_results= csv.writer(open("air_quality_test_results.csv", "ab+"), delimiter = ",")
            line_read = csv.reader("air_quality_test_results.csv", delimiter=",")
            line_count= len(open("air_quality_test_results.csv").readlines())

            # Add metadata if necessary
            if line_count==1:
                results.append("Date and Time")
                results.append("0.3 um")
                results.append("0.5 um")
                results.append("1.0 um")
                results.append("2.5 um")
                results.append("5.0 um")
                results.append("10 um")
                pen_results.writerow(results[0:6])
            results = []
            date_time = datetime.datetime
            results.append(date_time)
            results.append(repr(P3))
            results.append(repr(P5))
            results.append(repr(P10))
            results.append(repr(P25))
            results.append(repr(P50))
            results.append(repr(P100))
            pen_results.writerow(results[0:6])

        else:
            print('Check Sum Failed')
