import time
import datetime
import csv
import numpy as np
from matplotlib.dates import DateFormatter
import matplotlib.pyplot as plt
from collections import deque
import Adafruit_GPIO.SPI as SPI
import Adafruit_MCP3008

CLK  = 18
MISO = 23
MOSI = 24
CS   = 25

class adc_DAQ(object):
	def __init__(self):
		self.time_queue=deque()
		self.n_merge=5
		self.CO2_list=[]
		self.UV_list=[]
		self.time_list=[]
		self.maxdata=10
		self.CO2_queue=deque()
		self.UV_queue=deque()
		self.merge_test=False
		self.mcp=Adafruit_MCP3008.MCP3008(clk=CLK, cs=CS, miso=MISO, mosi=MOSI)

	def create_file(self):
		global adc_results
		file_time= time.strftime("%Y-%m-%d_%H-%M-%S", time.gmtime())
		filename = "/home/pi/data/CO2_test_results_"+file_time+".csv"
		adc_results=csv.writer(open(filename, "ab+"), delimiter = ",")
		metadata = []
		metadata.append("Date and Time")
		metadata.append("CO2 (ppm)")
		metadata.append("UV")
		adc_results.writerow(metadata[:])

	def start(self):
		global adc_results
		date_time = datetime.datetime.now()    
	
		# Read all the ADC channel values in a list.
		values = [0]*8
		for i in range(8):
			# The read_adc function will get the value of the specified channel (0-7).
			values[i] = self.mcp.read_adc(i)
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

		self.merge_test=False
		self.add_data(self.CO2_queue,self.CO2_list,concentration)
		self.add_data(self.UV_queue,self.UV_list,uv_index)
		self.add_time(self.time_queue, self.time_list, date_time)

		if self.merge_test==True:
			self.CO2_list=[]
			self.UV_list=[]
			self.time_list=[]

	def plot_CO2(self):
		if len(self.time_queue)>0:
			self.update_plot(1,self.time_queue,self.CO2_queue,"Time","Concentration (ppm)","Comcentration vs. time")    

	def plot_UV(self):
		if len(self.time_queue)>0:
			self.update_plot(2,self.time_queue,self.UV_queue,"Time","UV Index","UV vs.time")		

	def add_data(self, queue, temp_list, data):
		temp_list.append(data)
		if len(temp_list)>=self.n_merge:
			queue.append(np.mean(np.asarray(temp_list)))
			temp_list = []
		if len(queue)>self.maxdata:
			queue.popleft()	

	def update_plot(self,plot_id,xdata,ydata,xlabel,ylable,title):
		plt.ion()
		fig = plt.figure(plot_id)
		plt.clf()
		ax=fig.add_subplot(111)
		plt.xlabel(xlabel)
		plt.ylabel(ylable) 
		plt.title(title)
		plt.plot(xdata,ydata,"r.")
		fig.autofmt_xdate()
		ax.xaxis.set_major_formatter(DateFormatter('%H:%M:%S'))
		fig.show()
		plt.pause(0.0005)	

	def add_time(self, queue, timelist, data):
		print('Input time: {}'.format(data))
		timelist.append(data)
		if len(timelist)>=self.n_merge:
			self.merge_test=True
			queue.append(timelist[int((self.n_merge)/2)])
			print('Queue time: {}'.format(timelist[int((self.n_merge)/2)]))
			timelist=[]
		if len(queue)>self.maxdata:
			queue.popleft()    

	def close(self,plot_id):
         plt.close(plot_id)		
