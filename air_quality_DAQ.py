import time
import numpy as np
from collections import deque
import serial
import sys
import os
import pika
import json
import argparse
import csv

sys.stdout.flush()

class air_quality_DAQ():
    def __init__ (self, interval=1, datalog=None):
        # self.sensor = sensor [Not sure if this is necessary]
        self.port = serial.Serial("/dev/serial0", baudrate=9600, timeout=1.5)

        self.outfile_name = datalog

        self.n_merge = int(interval)
        self.PM01_list = []
        self.PM25_list = []
        self.PM10_list = []
        self.P3_list = []
        self.P5_list = []
        self.P10_list = []
        self.P25_list = []
        self.P50_list = []
        self.P100_list = []

        self.out_file = None

        if datalog is not None:
            self.create_file(datalog)


    def run(self):
        text = self.port.read(32)
        buffer = [ord(c) for c in text]
        if buffer[0] == 66:
            buf = buffer[1:32]

            # Get concentrations ug/m3
            PM01Val=repr((buf[3]<<8) + buf[4])
            PM25Val=repr((buf[5]<<8) + buf[6])
            PM10Val=repr((buf[7]<<8) + buf[8])

            # Get number of particles in 0.1 L of air above specific diameters
            P3  =repr((buf[15]<<8) + buf[16])
            P5  =repr((buf[17]<<8) + buf[18])
            P10 =repr((buf[19]<<8) + buf[20])
            P25 =repr((buf[21]<<8) + buf[22])
            P50 =repr((buf[23]<<8) + buf[24])
            P100=repr((buf[25]<<8) + buf[26])

            self.print_data(PM01Val,PM25Val,PM10Val,P3,P5,P10,P25,P50,P100)

            self.PM01_list.append(int(PM01Val))
            self.PM25_list.append(int(PM25Val))
            self.PM10_list.append(int(PM10Val))
            self.P3_list.append(int(P3))
            self.P5_list.append(int(P5))
            self.P10_list.append(int(P10))
            self.P25_list.append(int(P25))
            self.P50_list.append(int(P50))
            self.P100_list.append(int(P100))

            if len(self.PM25_list)>=self.n_merge:
                data1 = [np.mean(np.asarray(self.PM01_list)),
                         np.std(np.asarray(self.PM01_list))]
                data2 = [np.mean(np.asarray(self.PM25_list)),
                         np.std(np.asarray(self.PM25_list))]
                data3 = [np.mean(np.asarray(self.PM10_list)),
                         np.std(np.asarray(self.PM10_list))]
                self.send_data([data1,data2,data3])
                print("sent data to GUI")
                if self.out_file is not None:
                    self.write_data(data1, data2, data3)
                self.clear_data()
                sys.stdout.flush()


    def send_data(self, data):
		connection = pika.BlockingConnection(
                          pika.ConnectionParameters('localhost'))
		channel = connection.channel()
		channel.queue_declare(queue='toGUI')
		message = {'id': 'Air Quality', 'data': data}

		channel.basic_publish(exchange='',
							  routing_key='toGUI',
							  body=json.dumps(message))
		connection.close()


    def clear_data(self):
        self.P3_list[:] = []
        self.P5_list[:] = []
        self.P10_list[:] = []
        self.P25_list[:] = []
        self.P50_list[:] = []
        self.P100_list[:] = []
        self.PM01_list[:] = []
        self.PM25_list[:] = []
        self.PM10_list[:] = []


    def print_data(self,PM01Val,PM25Val,PM10Val,P3,P5,P10,P25,P50,P100):
        print('Concentration of Particulate Matter [ug/m3]')
        print('PM 1.0 = {} ug/m3'.format(PM01Val))
        print('PM 2.5 = {} ug/m3'.format(PM25Val))
        print('PM 10  = {} ug/m3\n'.format(PM25Val))
        print('')
        print('')
        #print('Number of particles in 0.1 L of air with specific diameter\n')
        #print('#Particles, diameter over 0.3 um = {}'.format(P3))
        #print('#Particles, diameter over 0.5 um = {}'.format(P5))
        #print('#Particles, diameter over 1.0 um = {}'.format(P10))
        #print('#Particles, diameter over 2.5 um = {}'.format(P25))
        #print('#Particles, diameter over 5.0 um = {}'.format(P50))
        #print('#Particles, diameter over 10  um = {}'.format(P100))
        sys.stdout.flush()


    def receive(self):
        connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
        channel = connection.channel()
        channel.queue_declare(queue='fromGUI')
        method_frame, header_frame, body = channel.basic_get(queue='fromGUI')
        if body is not None:
            message = json.loads(body)
            if message['id']=='Air Quality':
                channel.basic_ack(delivery_tag=method_frame.delivery_tag)
                connection.close()
                return message['cmd']
            else:
                connection.close()
                return None
        else:
            connection.close()
            return None

    def create_file(self, fname = None):
        self.out_file = open(fname, "ab+", buffering=0)
        self.results = csv.writer(self.out_file, delimiter = ",")
        metadata = ["Time", "0.3 um", "0.5 um", "1.0 um",
                    "2.5 um", "5.0 um", "10 um",
                    "PM 1.0", "PM 2.5", "PM 10"]
        self.results.writerow(metadata)

    def write_data(self, data1, data2, data3):
        this_time = time.time()
        self.results.writerow([this_time] + data1[:] + data2[:] + data3[:])

    def close_file(self):
        self.out_file.close()
        print("Copying data from {} to server.".format(self.out_file.name))
        sys_cmd = 'scp {} pi@192.168.4.1:/home/pi/data/'.format(
                                self.out_file.name)
        err = os.system(sys_cmd)
        print("system command returned {}".format(err))
        sys.stdout.flush()

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--interval", "-i", type=int, default=1)
    parser.add_argument('--datalog', '-d', default=None)

    args = parser.parse_args()
    arg_dict = vars(args)

    daq = air_quality_DAQ(**arg_dict)
    while True:
        # Look for messages from GUI every 10 ms
        msg = daq.receive()
        print("received msg: {}".format(msg))
        sys.stdout.flush()

        # If START is sent, begin running daq
		#    - collect data every second
		#    - re-check for message from GUI
        if msg == 'START':
            print("Inside START")
            while msg is None or msg=='START':
                print("running daq")
                daq.run()
                time.sleep(1)
                msg = daq.receive()
                sys.stdout.flush()
        # If EXIT is sent, break out of while loop and exit program
        if msg == 'STOP':
            print("stopping and entering exterior while loop.")
            sys.stdout.flush()

        if msg == 'EXIT':
            print('exiting program')
            print('logging data flag is {}'.format(arg_dict['datalog']))
            sys.stdout.flush()
            if arg_dict['datalog'] is not None:
                print("Closing log file and sending to server...")
                sys.stdout.flush()
                daq.close_file()
            break

        time.sleep(.2)

	exit
