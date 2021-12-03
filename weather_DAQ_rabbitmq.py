import time
import datetime
import csv
import numpy as np

import board
import time
from adafruit_bme280 import basic as adafruit_bme280

import sys
import os
import subprocess
import argparse
import pika
import json
sys.stdout.flush()

class weather_DAQ(object):
    def __init__(self, interval=1, datalog=None):
        self.n_merge=int(interval)

        self.outfile_name = datalog

        self.temp_list=[]
        self.humid_list=[]
        self.press_list=[]
        i2c = board.I2C()
        self.sensor = adafruit_bme280.Adafruit_BME280_I2C(i2c)

        self.out_file = None

        if datalog is not None:
            self.create_file(datalog)


    def run(self):
        sys.stdout.flush()
        try:
            degrees = self.sensor.temperature
            pascals = self.sensor.pressure
            atm = pascals/101325.0 * 100
            humidity = self.sensor.relative_humidity
            altitude = self.sensor.altitude

            self.temp_list.append(degrees)
            self.humid_list.append(humidity)
            self.press_list.append(atm)


            if len(self.temp_list)>=self.n_merge:
                t_data = [np.mean(np.asarray(self.temp_list)),
                           np.std(np.asarray(self.temp_list))]
                h_data = [np.mean(np.asarray(self.humid_list)),
                           np.std(np.asarray(self.humid_list))]
                p_data = [np.mean(np.asarray(self.press_list)),
                           np.std(np.asarray(self.press_list))]
                self.send_data('P/T/H',[t_data,h_data,p_data])
                print("Data being sent to GUI: {}".format([t_data,h_data,p_data]))
                if self.out_file is not None:
                    self.write_data(t_data, h_data, p_data)
                sys.stdout.flush()
                self.clear_data()

        except Exception as e:
            print("Error: could not read sensor data from {}".format(self.sensor))
            print(e)
            pass

    def send_data(self, data_type, data):
        connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
        channel = connection.channel()
        channel.queue_declare(queue='toGUI')
        message = {'id': data_type, 'data': data}

        channel.basic_publish(exchange='',
                              routing_key='toGUI',
                              body=json.dumps(message))
        connection.close()


    def clear_data(self):
        self.temp_list[:] = []
        self.humid_list[:] = []
        self.press_list[:] = []


    def receive(self):
        connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
        channel = connection.channel()
        channel.queue_declare(queue='fromGUI')
        method_frame, header_frame, body = channel.basic_get(queue='fromGUI')
        if body is not None:
            message = json.loads(body.decode('utf-8'))
            if message['id']=='P/T/H':
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
        self.out_file = open(fname, "a",newline="")
        self.results = csv.writer(self.out_file, delimiter = ",")
        metadata = ["Time", "Temperature", "T Unc.", "Humidity", "H Unc.", "Pressure", "P Unc."]
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

    daq = weather_DAQ(**arg_dict)
    while True:
        # Look for messages from GUI every 10 ms
        msg = daq.receive()
        print("P/T/H received msg: {}".format(msg))
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
            sys.stdout.flush()
            break

        time.sleep(.2)

    exit
