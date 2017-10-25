# Simple example of reading the MCP3008 analog input channels and printing
# them all out.
# Author: Tony DiCola
# License: Public Domain
import time
import datetime
import csv
import sys

# Import SPI library (for hardware SPI) and MCP3008 library.
import Adafruit_GPIO.SPI as SPI
import Adafruit_MCP3008

sys.stdout.flush()

# Software SPI configuration:
CLK  = 18
MISO = 23
MOSI = 24
CS   = 25
mcp = Adafruit_MCP3008.MCP3008(clk=CLK, cs=CS, miso=MISO, mosi=MOSI)

# Hardware SPI configuration:
# SPI_PORT   = 0
# SPI_DEVICE = 0
# mcp = Adafruit_MCP3008.MCP3008(spi=SPI.SpiDev(SPI_PORT, SPI_DEVICE))
print('Reading MCP3008 values, press Ctrl-C to quit...')
# Print nice channel column headers.
print('| {0:>4} | {1:>4} | {2:>4} | {3:>4} | {4:>4} | {5:>4} | {6:>4} | {7:>4} |'.format(*range(8)))
print('-' * 57)

file_time= time.strftime("%Y-%m-%d_%H-%M-%S", time.gmtime())
filename = "CO2_test_results_"+file_time+".csv"
adc_results = csv.writer(open(filename, "ab+"), delimiter = ",")

logfilename = "CO2_test_results.csv"
logresults = open(logfilename, "wb+", 0)

metadata = []
metadata.append("Date and Time")
metadata.append("CO2 (ppm)")
metadata.append("UV")
adc_results.writerow(metadata[:])
logresults.write(metadata[0]+","+metadata[1]+","+metadata[2]+"\n")

# Main program loop.
while True:
    date_time = datetime.datetime.now()
    # Read all the ADC channel values in a list.
    values = [0]*8
    for i in range(8):
        # The read_adc function will get the value of the specified channel (0-7).
        values[i] = mcp.read_adc(i)
    # Print the ADC values.
    # print('| {0:>4} | {1:>4} | {2:>4} | {3:>4} | {4:>4} | {5:>4} | {6:>4} | {7:>4} |'.format(*values))
    print('| {0:>4} | {1:>4} |'.format(values[0],values[7]))
    concentration = 5000/496*values[0] - 1250
    print('|{}|'.format(concentration))
    # Pause for half a second.
    uv_index = values[7]
    results = []
    results.append(date_time)
    results.append(concentration)
    results.append(uv_index)

    adc_results.writerow(results[:])
    logresults.write(datetime.datetime.strftime(results[0], "%Y-%m-%d %H:%M:%S")+","+str(results[1])+","+str(results[2])+"\n")

    time.sleep(1)
