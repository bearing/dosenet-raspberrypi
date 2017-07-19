# July 18th, 2017 15:49
# Code by Jennifer Atkins
# Based off of code by Ludi Cao

import time
import datetime
import csv
import os
from appJar import gui
import numpy as np
import dateutil
from matplotlib.dates import DateFormatter
import matplotlib.pyplot as plt
from collections import deque
import serial
import binascii

#sensor = entercodehere(morestuff) [Not sure if this is necessary] 

class air_quality_DAQ(object):
	def __init__ (self):
		# self.sensor = sensor [Not sure if this is necessary]
		self.running = False
		self.time_queue = deque()
		self.PM01_queue = deque()
		self.PM25_queue = deque()
		self.PM10_queue = deque()
		self.P3_queue = deque()
		self.P5_queue = deque()
		self.P10_queue = deque()
		self.P25_queue = deque()
		self.P50_queue = deque()
		self.P100_queue = deque()
		self.maxdata = 10
		self.n_merge = 5
		self.PM01_list = []
		self.PM25_list = []
		self.PM10_list = []
		self.P3_list = []
		self.P5_list = []
		self.P10_list = []
		self.P25_list = []
		self.P50_list = []
		self.P100_list = []
		self.time_list = []
		self.merge_test=False

	def create_file(self):
		global results
		file_time = time.strftime("%Y-%m-%d_%H-%M-%S", time.gmtime())
		filename = "air_quality_test_results_"+file_time+".csv"
		results = csv.writer(open(filename, "ab+"), delimiter = ",")
		metadata = ["Time", "0.3 um", "0.5 um", "1.0 um", "2.5 um", "5.0 um", "10 um", "PM 1.0", "PM 2.5", "PM 10"]
		results.writerow(metadata)

	def start(self):
		global results
		date_time = datetime.datetime.now()
		port = serial.Serial("/dev/ttyS0", baudrate=9600, timeout=1.5)
		text = port.read(32)
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

			print('\nConcentration of Particulate Matter [ug/m3]\n')
			print('PM 1.0 = {} ug/m3'.format(PM01Val))
			print('PM 2.5 = {} ug/m3'.format(PM25Val))
			print('PM 10  = {} ug/m3'.format(PM25Val))

			# Print number of particles in 0.1 L of air over specific diamaters
			print('Number of particles in 0.1 L of air with specific diameter\n')
			print('#Particles, diameter over 0.3 um = {}'.format(P3))
			print('#Particles, diameter over 0.5 um = {}'.format(P5))
			print('#Particles, diameter over 1.0 um = {}'.format(P10))
			print('#Particles, diameter over 2.5 um = {}'.format(P25))
			print('#Particles, diameter over 5.0 um = {}'.format(P50))
			print('#Particles, diameter over 10  um = {}'.format(P100))

			data = []
			data.append(date_time)
			data.append(PM01Val)
			data.append(PM25Val)
			data.append(PM10Val)
			data.append(P3)
			data.append(P5)
			data.append(P10)
			data.append(P25)
			data.append(P50)
			data.append(P100)

			results.writerow(data)

			self.merge_test = False
			self.add_data(self.PM01_queue,self.PM01_list,int(PM01Val))
			self.add_data(self.PM25_queue,self.PM25_list,int(PM25Val))
			self.add_data(self.PM10_queue,self.PM10_list,int(PM10Val))
			self.add_data(self.P3_queue,self.P3_list,int(P3))
			self.add_data(self.P5_queue,self.P5_list,int(P5))
			self.add_data(self.P10_queue,self.P10_list,int(P10))
			self.add_data(self.P25_queue,self.P25_list,int(P25))
			self.add_data(self.P50_queue,self.P50_list,int(P50))
			self.add_data(self.P100_queue,self.P100_list,int(P100))
			self.add_time(self.time_queue, self.time_list, date_time)

			if self.merge_test==True:
				self.PM01_list=[]
				self.PM25_list=[]
				self.PM10_list=[]
				self.P3_list=[]
				self.P5_list=[]
				self.P10_list=[]
				self.P25_list=[]
				self.P50_list=[]
				self.P100_list=[]


			if len(self.time_queue)>0:
				self.update_plot(1,self.time_queue,self.PM01_queue,"Time","PM 1.0 (ug/m3)","PM 1.0 vs. time")
				self.update_plot(2,self.time_queue,self.PM25_queue,"Time","PM 2.5 (ug/m3)","PM 2.5 vs. time")
				self.update_plot(3,self.time_queue,self.PM10_queue,"Time","PM 10 (ug/m3)","PM 10 vs. time")
				self.update_plot(4,self.time_queue,self.P3_queue,"Time","Particles, diameter over 0.3 um","Particles over 0.3 um vs. time")
				self.update_plot(5,self.time_queue,self.P5_queue,"Time","Particles, diameter over 0.5 um","Particles over 0.5 um vs. time")
				self.update_plot(6,self.time_queue,self.P10_queue,"Time","Particles, diameter over 1.0 um","Particles over 1.0 um vs. time")
				self.update_plot(7,self.time_queue,self.P25_queue,"Time","Particles, diameter over 2.5 um","Particles over 2.5 um vs. time")
				self.update_plot(8,self.time_queue,self.P50_queue,"Time","Particles, diameter over 5.0 um","Particles over 5.0 um vs. time")
				self.update_plot(9,self.time_queue,self.P100_queue,"Time","Particles, diameter over 10 um","Particles over 10 um vs. time")

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


	def add_data(self, queue, datalist, data):
		datalist.append(data)
		if len(datalist)>=self.n_merge:
			queue.append(np.mean(np.asarray(datalist)))
			datalist = []
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

	def plotdata(self):
		times = []
		PM01Val_list = []
		PM25Val_list = []
		PM10Val_list = []
		P3Val_list = []
		P5Val_list = []
		P10Val_list = []
		P25Val_list = []
		P50Val_list = []
		P100Val_list = []
		PM01Val_ave = []
		PM25Val_ave = []
		PM10Val_ave = []
		P3Val_ave = []
		P5Val_ave = []
		P10Val_ave = []
		P25Val_ave = []
		P50Val_ave = []
		P100Val_ave = []
		PM01Val_unc = []
		PM25Val_unc = []
		PM10Val_unc = []
		P3Val_unc = []
		P5Val_unc = []
		P10Val_unc = []
		P25Val_unc = []
		P50Val_unc = []
		P100Val_unc = []
		merge_times = []

		app=gui("Air Quality Plot","800x400")
		app.addLabel("1","Please choose a following .csv file")
		file_name=[]
		for filename in os.listdir('.'):
			if filename.endswith(".csv"):
				file_name.append(os.path.join('.', filename))
		app.setFont(20)
		app.addOptionBox("Files",file_name)
		app.setOptionBoxHeight("Files","4")
		app.addLabel("2","Enter the number of data points to merge:")
		app.setLabelFont("20","Heletica")
		app.addNumericEntry("n")
		app.setFocus("n")  
		n_merge=int(app.getEntry("n"))
		user_file=app.getOptionBox("Files")
		results = csv.reader(open(user_file), delimiter=',')

		def ok(btn):
			global row_counter
			row_counter = 0
			def pm01(btn):
				global row_counter

				for r in results:
					if row_counter>0:
						times.append(dateutil.parser.parse(r[0]))
						PM01Val_list.append(float(r[1]))
				
					row_counter+=1
			 
				global nsum_data
				ndata = int(len(PM01Val_list))
				nsum_data = int(ndata/n_merge)
				
				for i in range(nsum_data):
					ipm01 = PM01Val_list[i*n_merge:(i+1)*n_merge]
					ipm01_array = np.asarray(ipm01)
					pm01_mean = np.mean(ipm01_array)
					pm01_sigma = np.sqrt(np.var(ipm01_array))
					PM01Val_ave.append(pm01_mean)
					PM01Val_unc.append(pm01_sigma)
			
				for i in range(nsum_data):
					itimes = times[i*n_merge:(i+1)*n_merge]
					itime = itimes[int(len(itimes)/2)]
					merge_times.append(itime)

				fig=plt.figure()
				ax=fig.add_subplot(111)   
				plt.plot(merge_times, PM01Val_ave, "b.")
				plt.errorbar(merge_times, PM01Val_ave, yerr = PM01Val_unc)
				plt.title("PM 1.0")
				plt.xlabel("Time(s)")
				plt.ylabel("PM 1.0 (ug/m3)")
				fig.autofmt_xdate()
				ax.xaxis.set_major_formatter(DateFormatter('%H:%M:%S'))
				plt.show()
			def pm25(btn):
				global row_counter

				for r in results:
					if row_counter>0:
						times.append(dateutil.parser.parse(r[0]))
						PM25Val_list.append(float(r[1]))
				
					row_counter+=1
			 
				global nsum_data
				ndata = int(len(PM25Val_list))
				nsum_data = int(ndata/n_merge)
				
				for i in range(nsum_data):
					ipm25 = PM25Val_list[i*n_merge:(i+1)*n_merge]
					ipm25_array = np.asarray(ipm25)
					pm25_mean = np.mean(ipm25_array)
					pm25_sigma = np.sqrt(np.var(ipm25_array))
					PM25Val_ave.append(pm25_mean)
					PM25Val_unc.append(pm25_sigma)
			
				for i in range(nsum_data):
					itimes = times[i*n_merge:(i+1)*n_merge]
					itime = itimes[int(len(itimes)/2)]
					merge_times.append(itime)

				fig=plt.figure()
				ax=fig.add_subplot(111)   
				plt.plot(merge_times, PM25Val_ave, "b.")
				plt.errorbar(merge_times, PM25Val_ave, yerr = PM25Val_unc)
				plt.title("PM 2.5")
				plt.xlabel("Time(s)")
				plt.ylabel("PM 2.5 (ug/m3)")
				fig.autofmt_xdate()
				ax.xaxis.set_major_formatter(DateFormatter('%H:%M:%S'))
				plt.show()
			def pm10(btn):
				global row_counter

				for r in results:
					if row_counter>0:
						times.append(dateutil.parser.parse(r[0]))
						PM10Val_list.append(float(r[1]))
				
					row_counter+=1
			 
				global nsum_data
				ndata = int(len(PM10Val_list))
				nsum_data = int(ndata/n_merge)
				
				for i in range(nsum_data):
					ipm10 = PM10Val_list[i*n_merge:(i+1)*n_merge]
					ipm10_array = np.asarray(ipm10)
					pm10_mean = np.mean(ipm10_array)
					pm10_sigma = np.sqrt(np.var(ipm10_array))
					PM10Val_ave.append(pm10_mean)
					PM10Val_unc.append(pm10_sigma)
			
				for i in range(nsum_data):
					itimes = times[i*n_merge:(i+1)*n_merge]
					itime = itimes[int(len(itimes)/2)]
					merge_times.append(itime)

				fig=plt.figure()
				ax=fig.add_subplot(111)   
				plt.plot(merge_times, PM10Val_ave, "b.")
				plt.errorbar(merge_times, PM10Val_ave, yerr = PM10Val_unc)
				plt.title("PM 10")
				plt.xlabel("Time(s)")
				plt.ylabel("PM 10 (ug/m3)")
				fig.autofmt_xdate()
				ax.xaxis.set_major_formatter(DateFormatter('%H:%M:%S'))
				plt.show()
			def p3(btn):
				global row_counter

				for r in results:
					if row_counter>0:
						times.append(dateutil.parser.parse(r[0]))
						Val_list.append(float(r[1]))
				
					row_counter+=1
			 
				global nsum_data
				ndata = int(len(P3Val_list))
				nsum_data = int(ndata/n_merge)
				
				for i in range(nsum_data):
					ip3 = P3Val_list[i*n_merge:(i+1)*n_merge]
					ip3_array = np.asarray(ip3)
					p3_mean = np.mean(ip3_array)
					p3_sigma = np.sqrt(np.var(ip3_array))
					P3Val_ave.append(p3_mean)
					P3Val_unc.append(p3_sigma)
			
				for i in range(nsum_data):
					itimes = times[i*n_merge:(i+1)*n_merge]
					itime = itimes[int(len(itimes)/2)]
					merge_times.append(itime)

				fig=plt.figure()
				ax=fig.add_subplot(111)   
				plt.plot(merge_times, P3Val_ave, "b.")
				plt.errorbar(merge_times, P3Val_ave, yerr = P3Val_unc)
				plt.title("Particles over 0.3 um in diameter")
				plt.xlabel("Time(s)")
				plt.ylabel("Particles over 0.3 um")
				fig.autofmt_xdate()
				ax.xaxis.set_major_formatter(DateFormatter('%H:%M:%S'))
				plt.show()
			def p5(btn):
				global row_counter

				for r in results:
					if row_counter>0:
						times.append(dateutil.parser.parse(r[0]))
						Val_list.append(float(r[1]))
				
					row_counter+=1
			 
				global nsum_data
				ndata = int(len(P5Val_list))
				nsum_data = int(ndata/n_merge)
				
				for i in range(nsum_data):
					ip5 = P5Val_list[i*n_merge:(i+1)*n_merge]
					ip5_array = np.asarray(ip5)
					p5_mean = np.mean(ip5_array)
					p5_sigma = np.sqrt(np.var(ip5_array))
					P5Val_ave.append(p5_mean)
					P5Val_unc.append(p5_sigma)
			
				for i in range(nsum_data):
					itimes = times[i*n_merge:(i+1)*n_merge]
					itime = itimes[int(len(itimes)/2)]
					merge_times.append(itime)

				fig=plt.figure()
				ax=fig.add_subplot(111)   
				plt.plot(merge_times, P5Val_ave, "b.")
				plt.errorbar(merge_times, P5Val_ave, yerr = P5Val_unc)
				plt.title("Particles over 0.5 um in diameter")
				plt.xlabel("Time(s)")
				plt.ylabel("Particles over 0.5 um")
				fig.autofmt_xdate()
				ax.xaxis.set_major_formatter(DateFormatter('%H:%M:%S'))
				plt.show()
			def p10(btn):
				global row_counter

				for r in results:
					if row_counter>0:
						times.append(dateutil.parser.parse(r[0]))
						Val_list.append(float(r[1]))
				
					row_counter+=1
			 
				global nsum_data
				ndata = int(len(P10Val_list))
				nsum_data = int(ndata/n_merge)
				
				for i in range(nsum_data):
					ip10 = P10Val_list[i*n_merge:(i+1)*n_merge]
					ip10_array = np.asarray(ip10)
					p10_mean = np.mean(ip10_array)
					p10_sigma = np.sqrt(np.var(ip10_array))
					P10Val_ave.append(p10_mean)
					P10Val_unc.append(p10_sigma)
			
				for i in range(nsum_data):
					itimes = times[i*n_merge:(i+1)*n_merge]
					itime = itimes[int(len(itimes)/2)]
					merge_times.append(itime)

				fig=plt.figure()
				ax=fig.add_subplot(111)   
				plt.plot(merge_times, P10Val_ave, "b.")
				plt.errorbar(merge_times, P10Val_ave, yerr = P10Val_unc)
				plt.title("Particles over 1.0 um in diameter")
				plt.xlabel("Time(s)")
				plt.ylabel("Particles over 1.0 um")
				fig.autofmt_xdate()
				ax.xaxis.set_major_formatter(DateFormatter('%H:%M:%S'))
				plt.show()
			def p25(btn):
				global row_counter

				for r in results:
					if row_counter>0:
						times.append(dateutil.parser.parse(r[0]))
						Val_list.append(float(r[1]))
				
					row_counter+=1
			 
				global nsum_data
				ndata = int(len(P25Val_list))
				nsum_data = int(ndata/n_merge)
				
				for i in range(nsum_data):
					ip25 = P25Val_list[i*n_merge:(i+1)*n_merge]
					ip25_array = np.asarray(ip25)
					p25_mean = np.mean(ip25_array)
					p25_sigma = np.sqrt(np.var(ip25_array))
					P25Val_ave.append(p25_mean)
					P25Val_unc.append(p25_sigma)
			
				for i in range(nsum_data):
					itimes = times[i*n_merge:(i+1)*n_merge]
					itime = itimes[int(len(itimes)/2)]
					merge_times.append(itime)

				fig=plt.figure()
				ax=fig.add_subplot(111)   
				plt.plot(merge_times, P25Val_ave, "b.")
				plt.errorbar(merge_times, P25Val_ave, yerr = P25Val_unc)
				plt.title("Particles over 2.5 um in diameter")
				plt.xlabel("Time(s)")
				plt.ylabel("Particles over 2.5 um")
				fig.autofmt_xdate()
				ax.xaxis.set_major_formatter(DateFormatter('%H:%M:%S'))
				plt.show()
			def p50(btn):
				global row_counter

				for r in results:
					if row_counter>0:
						times.append(dateutil.parser.parse(r[0]))
						Val_list.append(float(r[1]))
				
					row_counter+=1
			 
				global nsum_data
				ndata = int(len(P50Val_list))
				nsum_data = int(ndata/n_merge)
				
				for i in range(nsum_data):
					ip50 = P50Val_list[i*n_merge:(i+1)*n_merge]
					ip50_array = np.asarray(ip50)
					p50_mean = np.mean(ip50_array)
					p50_sigma = np.sqrt(np.var(ip50_array))
					P50Val_ave.append(p50_mean)
					P50Val_unc.append(p50_sigma)
			
				for i in range(nsum_data):
					itimes = times[i*n_merge:(i+1)*n_merge]
					itime = itimes[int(len(itimes)/2)]
					merge_times.append(itime)

				fig=plt.figure()
				ax=fig.add_subplot(111)   
				plt.plot(merge_times, P50Val_ave, "b.")
				plt.errorbar(merge_times, P50Val_ave, yerr = P50Val_unc)
				plt.title("Particles over 5.0 um in diameter")
				plt.xlabel("Time(s)")
				plt.ylabel("Particles over 5.0 um")
				fig.autofmt_xdate()
				ax.xaxis.set_major_formatter(DateFormatter('%H:%M:%S'))
				plt.show()
			def p100(btn):
				global row_counter

				for r in results:
					if row_counter>0:
						times.append(dateutil.parser.parse(r[0]))
						Val_list.append(float(r[1]))
				
					row_counter+=1
			 
				global nsum_data
				ndata = int(len(P100Val_list))
				nsum_data = int(ndata/n_merge)
				
				for i in range(nsum_data):
					ip100 = P100Val_list[i*n_merge:(i+1)*n_merge]
					ip100_array = np.asarray(ip100)
					p100_mean = np.mean(ip100_array)
					p100_sigma = np.sqrt(np.var(ip100_array))
					P100Val_ave.append(p100_mean)
					P100Val_unc.append(p100_sigma)
			
				for i in range(nsum_data):
					itimes = times[i*n_merge:(i+1)*n_merge]
					itime = itimes[int(len(itimes)/2)]
					merge_times.append(itime)

				fig=plt.figure()
				ax=fig.add_subplot(111)   
				plt.plot(merge_times, P100Val_ave, "b.")
				plt.errorbar(merge_times, P100Val_ave, yerr = P100Val_unc)
				plt.title("Particles over 10 um in diameter")
				plt.xlabel("Time(s)")
				plt.ylabel("Particles over 10 um")
				fig.autofmt_xdate()
				ax.xaxis.set_major_formatter(DateFormatter('%H:%M:%S'))
				plt.show()
			app.addButton("PM 1.0 List",pm01)
			app.addButton("PM 2.5 List",pm25)
			app.addButton("PM 10 List",pm10)
			app.addButton("Particles over 0.3 um List",p3)
			app.addButton("Particles over 0.5 um List",p5)
			app.addButton("Particles over 1.0 um List",p10)
			app.addButton("Particles over 2.5 um List",p25)
			app.addButton("Particles over 5.0 um List",p50)
			app.addButton("Particles over 10 um List",p100)
			app.setButtonWidth("OK","20")
			app.setButtonHeight("OK","4")
			app.setButtonFont("20","Helvetica")
			app.go() 


		app.addButton("OK",ok)
		app.setButtonWidth("OK","20")
		app.setButtonHeight("OK","4")
		app.setButtonFont("20","Helvetica")
		app.go()

