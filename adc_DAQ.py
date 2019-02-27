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
sys.stdout.flush()

CLK  = 18
MISO = 23
MOSI = 24
CS   = 25

class adc_DAQ(object):
    def __init__(self, maxdata, n_merge):
        self.time_queue=deque()
        self.n_merge=int(n_merge)
        self.CO2_list=[]
        self.UV_list=[]
        self.time_list=[]
        self.maxdata=int(maxdata)
        self.CO2_queue=deque()
        self.CO2_error=deque()
        self.UV_queue=deque()
        self.merge_test=False
        self.first_data = True
        self.last_time = None
        self.mcp=Adafruit_MCP3008.MCP3008(clk=CLK, cs=CS, miso=MISO, mosi=MOSI)
        self.adc_results = None
        self.adc_file = None
        print('N MERGE: {}'.format(n_merge) )

    def create_file(self, fname = None):
    	import csv
        if fname is None:
            file_time= time.strftime("%Y-%m-%d_%H-%M-%S", time.gmtime())
            id_info = []
            with open ('/home/pi/config/server_config.csv') as f:
            	reader = csv.reader(f)
            	for row in reader:
            		id_info.append(row)
            filename = "/home/pi/data/"+"_".join(row)+"_CO2"+file_time+".csv"
        else:
            filename = fname
        self.adc_file = open(filename, "ab+")
        self.adc_results=csv.writer(adc_file, delimiter = ",")
        metadata = []
        metadata.append("Date and Time")
        metadata.append("CO2 (ppm)")
        #metadata.append("UV")
        self.adc_results.writerow(metadata[:])

    def start(self):
        date_time = datetime.datetime.now()
        self.mcp=Adafruit_MCP3008.MCP3008(clk=CLK, cs=CS, miso=MISO, mosi=MOSI)

        # Read all the ADC channel values in a list.
        values = [0]*8
        try:
            for i in range(8):
                # read_adc gets the value of the specified channel (0-7).
                values[i] = self.mcp.read_adc(i)
            concentration = 5000/496*values[0] - 1250
            results = []
            results.append(date_time)
            results.append(concentration)

            self.merge_test=False
            self.add_data(self.CO2_queue,
                          self.CO2_error,
                          self.CO2_list,
                          concentration)
            self.add_time(self.time_queue, self.time_list, date_time)

            if self.merge_test==True:
                self.CO2_list=[]
                self.time_list=[]
            if self.first_data and len(self.CO2_queue) != 0:
                for i in range(len(self.CO2_queue)):
                    data = []
                    data.append(self.time_queue[i])
                    data.append(self.CO2_queue[i])
                    data.append(self.CO2_error[i])
                    if self.adc_results is not None:
                        self.adc_results.writerow(data)
                        self.adc_file.flush()

                self.last_time = data[0]
                self.first_data = False
            elif not self.first_data:
                try:
                    if self.time_queue[-1] != self.last_time:
                        data = []
                        data.append(self.time_queue[-1])
                        data.append(self.CO2_queue[-1])
                        data.append(self.CO2_error[-1])
                        if self.adc_results is not None:
                            self.adc_results.writerow(data)
                            self.adc_file.flush()

                        self.last_time = self.time_queue[-1]

                except IndexError:
                    pass

        except Exception as e:
            pass


    def add_data(self, queue, queue_error, temp_list, data):
        temp_list.append(data)
        if len(temp_list)>=self.n_merge:
        	temp_list = np.asarray(temp_list)
        	print(temp_list)
        	pre_mean = np.mean(temp_list)
        	pre_sd = np.std(temp_list)
        	print(pre_mean,pre_sd)
        	while pre_sd > 15.0:
        		temp_list = temp_list[np.logical_and(
                                         temp_list<(pre_mean+pre_sd),
                                         temp_list>(pre_mean-pre_sd))]
        		#print(temp_list)
        		pre_mean = np.mean(temp_list)
        		pre_sd = np.std(temp_list)
        		#print(pre_mean,pre_sd)

        	queue.append(np.mean(temp_list))
        	queue_error.append(np.std(temp_list))

        if len(queue)>self.maxdata:
            queue.popleft()
            queue_error.popleft()

    def close_file(self):
        sys_cmd = 'scp {} pi@192.168.4.1:/home/pi/data'.format(
                                                        self.adc_file.name)
        print(sys_cmd)
        os.system(sys_cmd)
        self.adc_file.close()

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


    def print_data(self,PM01Val,PM25Val,PM10Val,P3,P5,P10,P25,P50,P100):
        print('Concentration of Particulate Matter [ug/m3]')
        print('PM 1.0 = {} ug/m3'.format(PM01Val))
        print('PM 2.5 = {} ug/m3'.format(PM25Val))
        printt('#Particles, diameter over 5.0 um = {}'.format(P50))
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


