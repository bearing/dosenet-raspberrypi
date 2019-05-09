import time
import datetime
import csv
import numpy as np
from matplotlib.dates import DateFormatter
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
from collections import deque
import Adafruit_GPIO.SPI as SPI
import Adafruit_MCP3008
import sys
import os
import argparse
import pika
import json
sys.stdout.flush()

CLK  = 18
MISO = 23
MOSI = 24
CS   = 25
# input interval is in units of seconds, we call run methods every .1s
NRUN = 10

class adc_DAQ(object):
    def __init__(self, interval=1, datalog=None):
        self.n_merge=int(NRUN*interval)
        self.CO2_list=[]
        self.mcp=Adafruit_MCP3008.MCP3008(clk=CLK, cs=CS, miso=MISO, mosi=MOSI)
        self.out_file = None
        if datalog is not None:
            self.create_file(datalog)
        print('N MERGE: {}'.format(interval) )

    def create_file(self, fname):
        self.out_file = open(fname, "ab+", buffering=0)
        self.adc_results=csv.writer(self.out_file, delimiter = ",")
        self.adc_results.writerow(["Date and Time", "CO2 (ppm)", "unc."])

    def write_data(self, data):
        this_time = time.time()
        print("Writing to output file: {}".format([this_time] + data[:]))
        self.adc_results.writerow([this_time] + data[:])

    def run(self):
        self.mcp=Adafruit_MCP3008.MCP3008(clk=CLK, cs=CS, miso=MISO, mosi=MOSI)
        # Read all the ADC channel values in a list.
        values = [0]*8
        sys.stdout.flush()
        try:
            for i in range(8):
                # read_adc gets the value of the specified channel (0-7).
                values[i] = self.mcp.read_adc(i)
            concentration = 5000/496*values[0] - 1250
            self.CO2_list.append(concentration)

            #self.print_data(self.CO2_list)

            if len(self.CO2_list)>=self.n_merge:
                data = self.merge_data(self.CO2_list)
                #print("Data being sent to GUI: {}".format(data))
                if self.out_file is not None:
                    self.write_data(data)
                self.send_data(data)
                self.clear_data()

        except Exception as e:
            print("Error: could not read sensor data: {}".format(values))
            print(e)
            pass


    def merge_data(self, temp_list):
        temp_list = np.asarray(temp_list)
        pre_mean = np.mean(temp_list)
        pre_sd = np.std(temp_list)
        while pre_sd > 15.0:
            temp_list = temp_list[np.logical_and(
                                  temp_list<(pre_mean+pre_sd),
                                  temp_list>(pre_mean-pre_sd))]
            pre_mean = np.mean(temp_list)
            pre_sd = np.std(temp_list)
        return [np.mean(temp_list), np.std(temp_list)]

    def send_data(self, data):
		connection = pika.BlockingConnection(
                          pika.ConnectionParameters('localhost'))
		channel = connection.channel()
		channel.queue_declare(queue='toGUI')
		message = {'id': 'CO2', 'data': data}

		channel.basic_publish(exchange='',
							  routing_key='toGUI',
							  body=json.dumps(message))
		connection.close()


    def clear_data(self):
        self.CO2_list[:] = []


    def print_data(self,CO2_list):
        print('CO2 data: {}'.format(CO2_list))
        print('Ave CO2 concentration = {}'.format(np.mean(CO2_list)))
        sys.stdout.flush()


    def receive(self):
        connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
        channel = connection.channel()
        channel.queue_declare(queue='fromGUI')
        method_frame, header_frame, body = channel.basic_get(queue='fromGUI')
        if body is not None:
            message = json.loads(body)
            if message['id']=='CO2':
                channel.basic_ack(delivery_tag=method_frame.delivery_tag)
                connection.close()
                return message['cmd']
            else:
                connection.close()
                return None
        else:
            connection.close()
            return None


    def close_file(self):
        print("Copying data from {} to server.".format(self.out_file.name))
        sys.stdout.flush()
        sys_cmd = "sudo scp {} pi@192.168.4.1:/home/pi/data/".format(
                                self.out_file.name)
        print("System cmd {}".format(sys_cmd))
        sys.stdout.flush()
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

    daq = adc_DAQ(**arg_dict)
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
                time.sleep(1/float(NRUN))
                msg = daq.receive()
                sys.stdout.flush()
        # If EXIT is sent, break out of while loop and exit program
        if msg == 'STOP':
            print("stopping and entering exterior while loop.")

        if msg == 'EXIT':
            print('exiting program')
            if arg_dict['datalog'] is not None:
                daq.close_file()
            break

        time.sleep(.2)

	exit
