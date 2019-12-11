import time
import datetime
import csv
import numpy as np

import board
import digitalio
import busio
import time
import adafruit_bme280

import sys
import os
import subprocess
import argparse
import pika
import json
sys.stdout.flush()

class weather_DAQ(object):
    def __init__(self, interval=1):
        self.n_merge=int(interval)
        self.temp_list=[]
        self.humid_list=[]
        self.press_list=[]
        #self.sensor = BME280(t_mode=BME280_OSAMPLE_8, p_mode=BME280_OSAMPLE_8, h_mode=BME280_OSAMPLE_8)
        i2c = busio.I2C(board.SCL, board.SDA)
        self.sensor = adafruit_bme280.Adafruit_BME280_I2C(i2c)


    def run(self):
        sys.stdout.flush()
        try:
            degrees = self.sensor.temperature
            pascals = self.sensor.pressure
            atm = pascals/101325.0
            humidity = self.sensor.humidity
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
                self.send_data('Temperature',t_data)
                self.send_data('Humidity',h_data)
                self.send_data('Pressure',p_data)
                print("Data being sent to GUI: {}".format(data))
                sys.stdout.flush()
                self.clear_data()

        except Exception as e:
            print("Error: could not read sensor data: {}".format(values))
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
            if message['id']=='Weather' or 
               message['id']=='Temperature' or 
               message['id']=='Humidity' or 
               message['id']=='Pressure':
                channel.basic_ack(delivery_tag=method_frame.delivery_tag)
                connection.close()
                return message['cmd']
            else:
                connection.close()
                return None
        else:
            connection.close()
            return None


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--interval", "-i", type=int, default=1)

    args = parser.parse_args()
    arg_dict = vars(args)

    daq = weather_DAQ(**arg_dict)
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
            sys.stdout.flush()
            break

        time.sleep(.2)

    exit
