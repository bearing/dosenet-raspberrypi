import time
import datetime
import os
import argparse
import numpy as np
from sensor import Sensor
import sys
import pika
import json
sys.stdout.flush()


class pocket_geiger_DAQ(object):
    def __init__(self, interval=1):
        self.n_merge=int(interval)
        self.count_list=[]
        self.sensor = Sensor()
        print('N MERGE: {}'.format(self.n_merge) )

    def run(self):
        date_time = time.time()

        try:
            count_cpm,count_err = self.sensor.get_cpm(date_time-60,date_time)
            print('CPM = {}+/-{}'.format(count_cpm,count_err))
            self.merge_test=False

            self.count_list.append(count_cpm)

            if len(self.count_list) >= self.n_merge:
                self.print_data(self.count_list)
                data = [np.mean(np.asarray(self.count_list)),
                        np.std(np.asarray(self.count_list))]
                self.send_data(data)
                self.clear_data()

        except Exception as e:
            print(e)
            pass

    def send_data(self, data):
        connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
        channel = connection.channel()
        channel.queue_declare(queue='toGUI')
        message = {'id': 'Radiation', 'data': data}

        channel.basic_publish(exchange='',
                              routing_key='toGUI',
                              body=json.dumps(message))
        connection.close()


    def clear_data(self):
        self.count_list[:] = []


    def print_data(self,cpm_list):
        print('Radiation data: {}'.format(cpm_list))
        print('Ave CPM = {}'.format(np.mean(cpm_list)))
        sys.stdout.flush()


    def receive(self):
        connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
        channel = connection.channel()
        channel.queue_declare(queue='fromGUI')
        method_frame, header_frame, body = channel.basic_get(queue='fromGUI')
        if body is not None:
            message = json.loads(body.decode('utf-8'))
            if message['id']=='Radiation':
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

    daq = pocket_geiger_DAQ(**arg_dict)
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

        if msg == 'EXIT':
            print('exiting program')
            if arg_dict['datalog'] is not None:
                sys.stdout.flush()
                daq.close_file()
            break

        time.sleep(.2)

    exit
