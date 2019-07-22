import folium
from folium.plugins import FloatImage
import os
import time
import matplotlib.pyplot as plt
import matplotlib as mpl
import pika
from PyQt5.QtWidgets import *
import sys
from pylab import cm
from Adafruit_BME280 import *
import json
import gps
import datetime
import traceback
from PIL import Image
import csv

def receive(ID, queue):
	'''
	Returns command from queue with given ID
	'''
	connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
	channel = connection.channel()
	channel.queue_declare(queue=queue)
	method_frame, header_frame, body = channel.basic_get(queue=queue)
	if body is not None:
		message = json.loads(body)
		if message['id']==ID:
			channel.basic_ack(delivery_tag=method_frame.delivery_tag)
			connection.close()
			return message['cmd']
	else:
		connection.close()
		return None

def receive_last_message(ID, queue, message=''):
	'''
	Returns last consecutive message with matching ID.
	'''
	body = receive(ID, queue)
	while body != None:
		message = body
		body = receive(ID, queue)
	return message
	

def makecolormap(label,minvalue,maxvalue,filename):
	'''
	Makes a color map with given maximum and minimum values.
	'''
	fig, ax = plt.subplots(figsize=(6,1))
	fig.subplots_adjust(bottom=0.5)

	cmap = mpl.cm.rainbow ###########

	norm = mpl.colors.Normalize(vmin=minvalue, vmax=maxvalue)

	
	cb1 = mpl.colorbar.ColorbarBase(ax, cmap=cmap, norm=norm, orientation='horizontal')
	cb1.set_label(label)
	
	filename = (filename.replace(" ", "_").replace("/", "_")+'.png')
	
	fig.savefig(filename)
	
	colorbar = Image.open(filename)
	colorbar.crop((50, 0, 560, 100)).save(filename)

def establish_dict():
	
	sensor_dict = {}
	
	for sensor in active_sensors:
		if sensor == 'Air Quality PM 2.5 (ug/m3)':
			sensor_dict['Air Quality PM 2.5 (ug/m3)'] = {'min': 0, 'max':100, 'fg': '','val':0}		
			os.system('python air_quality_DAQ.py -i ' + str(int(time_delay * 0.5)) + ' &')
			
		elif sensor == 'CO2 (ppm)':
			sensor_dict['CO2 (ppm)'] = {'min': 300, 'max':1000, 'fg': '','val':0}
			os.system('python adc_DAQ.py -i ' + str(int(time_delay * 0.5)) + ' &')	
			
		elif sensor == 'Humidity (%)':
			sensor_dict['Humidity (%)'] = {'min': 30, 'max':60, 'fg': '','val':0}
			os.system('python weather_DAQ.py -i ' + str(time_delay)  + ' &')
					
		elif sensor == 'Pressure (Pa)':
			sensor_dict['Pressure (Pa)'] = {'min': 99500, 'max':101400, 'fg': '','val':0}
			os.system('python weather_DAQ.py -i ' + str(time_delay) + ' &')	
				
		elif sensor == 'Radiation (cps)':
			sensor_dict['Radiation (cps)'] = {'min': 0, 'max':100, 'fg': '','val':0}			
			os.system('python D3S_rabbitmq_DAQ.py -i ' + str(time_delay) + ' &')
			
		elif sensor == 'Temperature (C)':
			sensor_dict['Temperature (C)'] = {'min': 15, 'max':30, 'fg': '','val':0}
			os.system('python weather_DAQ.py -i ' + str(time_delay) + ' &')
	
	time.sleep(5)
	
	return sensor_dict
			
		
		
	
if __name__ == '__main__':
	#Initial variables
	sensor_tuple = ('Air Quality PM 2.5 (ug/m3)','CO2 (ppm)', 'Humidity (%)', 'Pressure (Pa)','Radiation (cps)', 'Temperature (C)')
	
	# Gets time delay, list of active sensors, and shown sensor
	time_delay = receive('Time Delay', 'control')
	active_sensors = receive('Sensors', 'control') # List of active sensors
	shown_sensor = receive_last_message('Shown Sensor', 'control')
	
	sensor_dict= establish_dict() # heh heh heh
	
	location = folium.Map(location=[37.875381,-122.259019],zoom_start = 15) # Fetches chunk
	location.save('testmap.html')
	
	os.system('xdg-open testmap.html') # Opens the window containing map
	time.sleep(5)
	
	for key in sensor_dict:	
		sensor_dict[key]['fg'] = folium.FeatureGroup(name=key) # Establishes Feature Groups
		sensor_dict[key]['fg'].add_to(location) # Adds featuregroup to map
		
		makecolormap(key,sensor_dict[key]['min'],sensor_dict[key]['max'],'colormap'+key) # Creates Colormap that will be used as a legend
	
	folium.LayerControl().add_to(location)
	
	text = '' # Initializing text
	
	######################################################################################### To Do: Get data from sensors and plot it - ezpz
	
	
	# Starts GPS DAQ
	os.system('python gps_daq.py -i' + time_delay + '&')
