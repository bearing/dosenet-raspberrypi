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
BME280_OSAMPLE_8 = 4
import json
import gps
import traceback
from PIL import Image
import csv

print("Starting map_plot.py. :)")

def sendmsg(ID,cmd,queue):
	'''
	Sends a message through the selected queue with the given ID.
	'''
	connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
	channel = connection.channel()

	channel.queue_declare(queue=queue)
	channel.basic_publish(exchange='', routing_key=queue, body=json.dumps({'id':ID, 'cmd':cmd}))
	connection.close()

def receive(ID, queue):
	'''
	Returns command or data from queue with given ID. If given ID is None, then returns first message from queue.
	'''
	connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
	channel = connection.channel()
	channel.queue_declare(queue=queue)
	method_frame, header_frame, body = channel.basic_get(queue=queue)
	if body is not None:
		message = json.loads(body.decode('utf-8'))
		if ID == None:
			channel.basic_ack(delivery_tag=method_frame.delivery_tag)
			connection.close()
			return message
		elif message['id'] == ID:
			channel.basic_ack(delivery_tag=method_frame.delivery_tag)
			connection.close()
			if 'cmd' in message:
				return message['cmd']
			elif 'data' in message:
				return message['data']
			else:
				print("Center of the earth")
				return None
		else:
			print("Inside")
			connection.close()
			return None
	else:
		print("Outside")
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

	cmap = mpl.cm.rainbow

	norm = mpl.colors.Normalize(vmin=minvalue, vmax=maxvalue)

	
	cb1 = mpl.colorbar.ColorbarBase(ax, cmap=cmap, norm=norm, orientation='horizontal')
	cb1.set_label(label)
	
	filename = (filename.replace(" ", "_").replace("/", "_")+'.png')
	
	fig.savefig(filename)
	
	colorbar = Image.open(filename)
	colorbar.crop((50, 0, 560, 100)).save(filename)

def popuptext(sensor_chosen):
	'''
	Formats text for popup labels
	'''
	# List for popup label (current time and values)
	popupv = ["Time: " + str(time.ctime(time.time())) + '<br>']
	
	for sensor in active_sensors: 
		if sensor == sensor_chosen:
			popupv.append(sensor+" (shown): ")
		else:
			popupv.append(sensor+": ")

		popupv.append(str(sensor_dict[sensor]['val']) + "<br>")
			
	return ''.join(popupv) # Joins the list of popup labels into a string

def establish_dict():
	'''
	Establishes dictionary of data points.
	'''
	sensor_dict = {}
	
	for sensor in active_sensors:
		if sensor == 'Air Quality PM 2.5 (ug/m3)':
			sensor_dict['Air Quality PM 2.5 (ug/m3)'] = {'min': 0, 'max':100, 'fg': '','val':0}		
			os.system('python air_quality_DAQ.py -i ' + str(int(time_delay * 0.5)) + ' &')
			sendmsg('Air Quality', 'START', 'fromGUI')
			
		elif sensor == 'CO2 (ppm)':
			sensor_dict['CO2 (ppm)'] = {'min': 300, 'max':1000, 'fg': '','val':0}
			os.system('python adc_DAQ.py -i ' + str(int(time_delay * 0.5)) + ' &')
			sendmsg('CO2', 'START', 'fromGUI')
			
		elif sensor == 'Humidity (%)':
			sensor_dict['Humidity (%)'] = {'min': 30, 'max':60, 'fg': '','val':0}
					
		elif sensor == 'Pressure (Pa)':
			sensor_dict['Pressure (Pa)'] = {'min': 99500, 'max':101400, 'fg': '','val':0}
				
		elif sensor == 'Radiation (cps)':
			sensor_dict['Radiation (cps)'] = {'min': 0, 'max':100, 'fg': '','val':0}			
			os.system('sudo python D3S_rabbitmq_DAQ.py -i ' + str(time_delay) + ' &')
			sendmsg('Radiation', 'START', 'fromGUI')
			
		elif sensor == 'Temperature (C)':
			sensor_dict['Temperature (C)'] = {'min': 15, 'max':30, 'fg': '','val':0}
	
	time.sleep(5)
	
	return sensor_dict

def read_data():
	'''
	Reads data into dictionary.
	'''
	data = receive(None, 'toGUI')
	
	while data != None:	# Reads data from queue
		sensor_label = data['id']
		
		if sensor_label == "Air Quality":
			sensor_dict[sensor_label + ' PM 2.5 (ug/m3)']['val'] = data['data'][1][0]
		elif sensor_label == "CO2":
			sensor_dict[sensor_label + ' (ppm)']['val'] = data['data'][0]
		elif sensor_label == "Radiation":
			global spectrum
			spectrum = data['data']
			counts = 0
			for value in data['data']:
				counts = counts + value 
			counts = counts/float(time_delay)
			sensor_dict[sensor_label + ' (cps)']['val'] = counts
		elif sensor_label == "GPS":
			global coordinates
			coordinates = data['data']
			
		data = receive(None, 'toGUI')
		
	if 'Humidity (%)' in active_sensors:
		weather_port = BME280(t_mode=BME280_OSAMPLE_8, p_mode=BME280_OSAMPLE_8, h_mode=BME280_OSAMPLE_8)
		temp_data = weather_port.read_temperature()
		pres_data = weather_port.read_pressure()
		sensor_dict['Humidity (%)']['val'] = weather_port.read_humidity()
	if 'Pressure (Pa)' in active_sensors:
		weather_port = BME280(t_mode=BME280_OSAMPLE_8, p_mode=BME280_OSAMPLE_8, h_mode=BME280_OSAMPLE_8)
		temp_data = weather_port.read_temperature()
		sensor_dict['Pressure (Pa)']['val'] = weather_port.read_pressure()
		humi_data = weather_port.read_humidity()
	if 'Temperature (C)' in active_sensors:
		weather_port = BME280(t_mode=BME280_OSAMPLE_8, p_mode=BME280_OSAMPLE_8, h_mode=BME280_OSAMPLE_8)
		sensor_dict['Temperature (C)']['val'] = weather_port.read_temperature()
		pres_data = weather_port.read_pressure()
		humi_data = weather_port.read_humidity()

def create_file():
	'''
	Creates csv file to log data from run - name contains acronym for all sensors used as well as timestamp (zyy of run intialization
	Returns open file and results
	'''
	global filename
	tempfileheader = ''
	if filename == '':
		for letter in active_sensors:
			tempfileheader = tempfileheader + letter[0]
	
		filename = (tempfileheader+' '+str(time.ctime(time.time()))).replace(' ', '_')
		print(filename)
		
	log_out_file = open('../../data/'+filename+'.csv', "a+", )
	log_results = csv.writer(log_out_file, delimiter = ",")
	log_results.writerow(['Epoch time', 'Latitude', 'Longitude'] + active_sensors)
	
	files = {'Data Log Out File': log_out_file, 'Data Log Results': log_results}
	
	if 'Radiation (cps)' in active_sensors:
		spectrum_out_file = open('../../data/' + str(time.ctime(time.time())) + ' spectrum.csv', "a+", )
		spectrum_results = csv.writer(spectrum_out_file, delimiter = ",")
		spectrum_results.writerow(['Epoch time'] + list(range(0,1024)))
		files['Spectrum Out File'] = spectrum_out_file
		files['Spectrum Results'] = spectrum_results
	return files

def write_data():
	'''
	Appends row to previously created log file 
	'''
	row = [time.time(), coordinates[0], coordinates[1]]
	for sensor in active_sensors:
		row.append(sensor_dict[sensor]['val'])
	files['Data Log Results'].writerow(row)
	
	if 'Radiation (cps)' in active_sensors:
		files['Spectrum Results'].writerow([time.time()] + spectrum)
		

def close_file():
	'''
	Closes the log file
	'''
	files['Data Log Out File'].close()
	
	if 'Radiation (cps)' in active_sensors:
		files['Spectrum Out File'].close()
	
	sys.stdout.flush()
	
if __name__ == '__main__':
	try:
		#Initial variables
		sensor_tuple = ('Air Quality PM 2.5 (ug/m3)','CO2 (ppm)', 'Humidity (%)', 'Pressure (Pa)','Radiation (cps)', 'Temperature (C)')
		coordinates = [0, 0]
		spectrum = []
		
		# Gets list of active sensors, time delay, and filename
		active_sensors = receive('Sensors', 'control') # List of active sensors
		time_delay = receive('Time Delay', 'control')
		filename = receive('Filename', 'control')
		print(active_sensors)
		
		sensor_dict = establish_dict() # Establishes a dictionary
		
		files = create_file()
		
		# Starts GPS DAQ
		os.system('python gps_daq.py -i' + str(time_delay) + '&')
		
		location = folium.Map(location=[37.875381,-122.259019],zoom_start = 15) # Fetches chunk
		location.save('testmap.html')
		
		os.system('xdg-open testmap.html') # Opens the window containing map
		time.sleep(5)
		
		for key in sensor_dict:	
			sensor_dict[key]['fg'] = folium.FeatureGroup(name=key) # Establishes Feature Groups
			sensor_dict[key]['fg'].add_to(location) # Adds featuregroup to map
			
			makecolormap(key,sensor_dict[key]['min'],sensor_dict[key]['max'],'colormap'+key) # Creates Colormap that will be used as a legend
		
		folium.LayerControl().add_to(location) # Adds layers to location
		
		shown_sensor = '' # Initializing shown_sensor
		
		while True:
			shown_sensor = receive_last_message('Shown Sensor', 'control', shown_sensor) # Gets the chosen sensor to visualize
			print(shown_sensor)
			
			if receive_last_message('EXIT', 'control') == 'EXIT': # Looks for EXIT command
				break
			
			read_data() # IMPORTANT FUNCTION -- Reads the data from queue
			
			location = folium.Map(location=[37.875381,-122.259019],zoom_start = 15)
			
			filepath = '/home/pi/dosenet-raspberrypi/gps/colormap'+shown_sensor.replace(" ", "_").replace("/", "_")+'.png' # Adds colormap to html file
			FloatImage(filepath, bottom = 5, left = 4).add_to(location)
			
			for key in sensor_dict:
				
				print (key + ": This is the show" + str(sensor_dict[key]['fg'].show))
				
				sensor_dict[key]['fg'].show =(bool(key == shown_sensor)) # Sets the selected sensor to visible
				
				sensor_dict[key]['fg'].add_to(location)

				print (key + ": This is the show after" + str(sensor_dict[key]['fg'].show))
				
				# Gets point color
				cmap = cm.get_cmap('rainbow',sensor_dict[key]['max']-sensor_dict[key]['min'])
				point_color = mpl.colors.rgb2hex(cmap(int(sensor_dict[key]['val']-sensor_dict[key]['min']))[:3])
				
				# Plots Circle
				folium.Circle(radius = 15, location=coordinates, popup = popuptext(key),
							fill_color = point_color,color = '#000000',fill_opacity = 1,stroke = 1,weight = 1).add_to(sensor_dict[key]['fg'])
							
		
			folium.LayerControl().add_to(location)
			
			write_data()
				
			location.save('testmap.html') # Saves map as html
			
			os.system('xdotool search --onlyvisible --name "Chromium" windowfocus key --clearmodifiers ctrl+r')
			
			time.sleep(time_delay)
	finally:
		close_file()
		
		os.system('xdotool search --onlyvisible --name "Chromium" windowfocus key --clearmodifiers ctrl+w')
		
		for sensor in active_sensors:
			if sensor not in ['Humidity (%)', 'Pressure (Pa)', 'Temperature (C)']:
				sendmsg(sensor.split(' PM')[0].split(' (')[0], 'EXIT','fromGUI')
		sendmsg('GPS', 'EXIT', 'fromGUI')
		
		traceback.print_exc()
	

