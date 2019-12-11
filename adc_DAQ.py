import time
import datetime
import numpy as np
import sys
import os
import argparse
import pika
import json

import busio
import board
import digitalio
import adafruit_mcp3xxx.mcp3008 as MCP
from adafruit_mcp3xxx.analog_in import AnalogIn

sys.stdout.flush()

CLK  = board.D21
MISO = board.D19
MOSI = board.D20
CS   = board.D26
# input interval is in units of seconds, we call run methods every .1s
NRUN = 10

class adc_DAQ(object):
    def __init__(self, interval=1):
        self.n_merge=int(NRUN*interval)
        self.CO2_list=[]
        spi = busio.SPI(clock=CLK, MISO=MISO, MOSI=MOSI)
        cs = digitalio.DigitalInOut(CS)
        self.mcp=MCP.MCP3008(spi,cs)
        self.channels = [0]*8
        self.channels[0] = AnalogIn(self.mcp, MCP.P0)
        self.channels[1] = AnalogIn(self.mcp, MCP.P1)
        self.channels[2] = AnalogIn(self.mcp, MCP.P2)
        self.channels[3] = AnalogIn(self.mcp, MCP.P3)
        self.channels[4] = AnalogIn(self.mcp, MCP.P4)
        self.channels[5] = AnalogIn(self.mcp, MCP.P5)
        self.channels[6] = AnalogIn(self.mcp, MCP.P6)
        self.channels[7] = AnalogIn(self.mcp, MCP.P7)
        print('N MERGE: {}'.format(interval) )

    def run(self):
        # Read all the ADC channel values in a list.
        values = [0]*8
        sys.stdout.flush()
        try:
            for i in range(8):
                # read_adc gets the value of the specified channel (0-7).
                values[i] = self.channels[i].value
            concentration = 5000/496*values[0] - 1250
            self.CO2_list.append(concentration)


            if len(self.CO2_list)>=self.n_merge:
                self.print_data(self.CO2_list)
                data = self.merge_data(self.CO2_list)
                #print("Data being sent to GUI: {}".format(data))
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
        connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
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


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--interval", "-i", type=int, default=1)

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
                sys.stdout.flush()
                daq.close_file()
            break

        time.sleep(.2)

    exit
