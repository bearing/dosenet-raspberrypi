'''
 (         )   (            )               
 )\ )   ( /(   )\ )      ( /(        *   )  
(()/(   )\()) (()/( (    )\()) (   ` )  /(  
 /(_)) ((_)\   /(_)))\  ((_)\  )\   ( )(_)) 
(_))_    ((_) (_)) ((_)  _((_)((_) (_(_())  
 |   \  / _ \ / __|| __|| \| || __||_   _|  
 | |) || (_) |\__ \| _| |  ` || _|   | |    
 |___/  \___/ |___/|___||_|\_||___|  |_|    
'''
# It might not look like it on github, but ALBERT QIANG worked on this too
# Please don't forget that
# It's all I have
import folium
from folium.plugins import FloatImage
import os
import time
import matplotlib.pyplot as plt
import matplotlib as mpl
import pika
from pylab import *
from PyQt5.QtWidgets import *
import sys
from Adafruit_BME280 import *
import json
import gps
import datetime
import traceback
from PIL import Image
import csv

def clear_queue(queue):
	'''
	Clears 'toGUI' and 'fromGUI' queues.
	'''
	connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
	channel = connection.channel()
	channel.queue_declare(queue=queue)
	channel.queue_delete(queue=queue)
	connection.close()

def start_sensor(queue, sensor):
	'''
	Starts collecting air quality data.
	'''
	sendmsg(json.dumps({'id':sensor, 'cmd': "START"}), queue)

def get_queued_data(queue, sensor, time_delay):
	'''
	Gets queued sensor data (Air Quality, CO2, Radiation)
	'''
	data = ''
	data = json.loads(getlastmsg(queue, data))
	
	if sensor == 'Air Quality':
		return data['data'][1][0]
	elif sensor == "CO2":
		return data['data'][0]
	elif sensor == 'Radiation':
		counts = 0
		for value in data['data']:
			counts = counts + value 
		counts = counts/float(time_delay)
		return counts

def read_data (sensor):
	'''
	Reads data from sensors. Add code here to add a new sensor.
	'''
####################################################################################################################################### Add code here for new sensor
	if sensor == sensor_array[0]:
		return get_queued_data('toGUI_aq', 'Air Quality', time_delay)
	elif sensor == sensor_array[1]:
		return get_queued_data('toGUI_CO2','CO2',time_delay)
	# All three values are read in for each value because the sensor is incapable of gathering pressure or humidity data before gathering temperature
	elif sensor == sensor_array[2]:
		weather_port = BME280(t_mode=BME280_OSAMPLE_8, p_mode=BME280_OSAMPLE_8, h_mode=BME280_OSAMPLE_8)
		temp_data = weather_port.read_temperature() 
		pres_data = weather_port.read_pressure()
		humi_data = weather_port.read_humidity()
		return humi_data
	elif sensor == sensor_array[3]:
		weather_port = BME280(t_mode=BME280_OSAMPLE_8, p_mode=BME280_OSAMPLE_8, h_mode=BME280_OSAMPLE_8)
		temp_data = weather_port.read_temperature()
		pres_data = weather_port.read_pressure()
		humi_data = weather_port.read_humidity()
		return pres_data
	elif sensor == sensor_array[4]:
		return get_queued_data('toGUI_d3s', 'Radiation', time_delay)
	elif sensor == sensor_array[5]:
		weather_port = BME280(t_mode=BME280_OSAMPLE_8, p_mode=BME280_OSAMPLE_8, h_mode=BME280_OSAMPLE_8)
		temp_data = weather_port.read_temperature()
		pres_data = weather_port.read_pressure()
		humi_data = weather_port.read_humidity()
		return temp_data
	
		
def stop_sensor(queue, sensor):
	'''
	Stops selected sensor by sending stop command through queue
	'''
	sendmsg(json.dumps({'id':sensor, 'cmd': "EXIT"}), queue)
	
def establish_dict(time_delay):
	'''
	Establishes the dictionary with all the sensor information. Time delay is needed to account for the bootup time of some sensor daq scripts. Add code here to add a new sensor.
	'''
	body = ''
	body = str(getlastmsg('sensor_list', body))
	sensors = str(body).split(',')
	sensor_dict = {}
	
######################################################################################################################################## Add code here for new sensor
	if sensor_array[0] in sensors:
		sensor_dict[sensor_array[0]] = [0, 100, 0] # Air Quality
		os.system('python aq_daq.py -i ' + str(int(time_delay * 0.5)) + ' &')
		clear_queue('toGUI_aq')
		clear_queue('fromGUI_aq')
		start_sensor('fromGUI_aq', 'Air Quality')
		
	if sensor_array[1] in sensors:
		sensor_dict[sensor_array[1]] = [300, 1000, 0] # CO2
		os.system('python adc_daq.py -i ' + str(int(0.5 * time_delay)) + ' &')
		clear_queue('toGUI_CO2')
		clear_queue('fromGUI_CO2')
		start_sensor('fromGUI_CO2', 'CO2')
		
	if sensor_array[2] in sensors:
		sensor_dict[sensor_array[2]] = [30, 60, 0] # Humidity
		
	if sensor_array[3] in sensors:
		sensor_dict[sensor_array[3]] = [99500, 101400, 0] # Pressure
		
	if sensor_array[4] in sensors:
		sensor_dict[sensor_array[4]] = [0, 100, 0] # Radiation
		os.system('sudo python d3s_daq.py -i ' + str(time_delay) + ' &')
		clear_queue('toGUI_d3s')
		clear_queue('fromGUI_d3s')
		start_sensor('fromGUI_d3s', 'Radiation')
		
	if sensor_array[5] in sensors:
		sensor_dict[sensor_array[5]] = [15, 30, 0] # Temperature
		
	time.sleep(time_delay) # Letting sensor daqs boot up
	return sensor_dict
	
def makecolormap(label,minvalue,maxvalue,filename):
	'''
	Makes a color map with given maximum and minimum values.
	'''
	fig, ax = plt.subplots(figsize=(6,1))
	fig.subplots_adjust(bottom=0.5)

	cmap = mpl.cm.spectral

	norm = mpl.colors.Normalize(vmin=minvalue, vmax=maxvalue)

	
	cb1 = mpl.colorbar.ColorbarBase(ax, cmap=cmap, norm=norm, orientation='horizontal')
	cb1.set_label(label)
	
	filename = (filename.replace(" ", "_").replace("/", "_")+'.png')
	
	fig.savefig(filename)
	
def cropcolorbar(filename):
	'''
	Crops the white space around the color bar
	'''
	colorbar = Image.open(filename)
	colorbar.crop((50, 0, 560, 100)).save(filename)

def localtime():
	'''
	Returns in 24 hr local time in the format: [Day of the week] [Month] [Date], [Year] @ [Hour]:[Minute]:[Second]
	Example: Thursday July 4, 1776 @ 16:21:09
	'''
	current_time = datetime.datetime.now()
	return current_time.strftime('%A') + ' ' + current_time.strftime('%B') + ' ' + current_time.strftime('%d') + ', ' + current_time.strftime('%Y') + ' @ ' + current_time.strftime('%H') + ':' + current_time.strftime('%M') + ':' + current_time.strftime('%S') + ' ' + current_time.strftime('%Z')
	
def sendmsg(s,queue):
	'''
	Sends a message through the selected queue.
	'''
	connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
	channel = connection.channel()

	channel.queue_declare(queue=queue)
	channel.basic_publish(exchange='', routing_key=queue, body=str(s))
	connection.close()

def getmsg(queue):
	'''
	Returns first body from queue and acknowledges it automatically.
	'''
	connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost')) 
	channel = connection.channel()
	channel.queue_declare(queue=queue)
	
	return channel.basic_get(queue=queue, auto_ack=True)[2]

def getlastmsg(queue, text):
	'''
	Returns last body from queue and acknowledges all of the bodies in queue
	'''
	while True:
		body = getmsg(queue)
		if str(body) == 'None':
			break
		text=str(body)
	return text
	
def create_file():
	'''
	Creates csv file to log data from run - name contains acronym for all sensors used as well as timestamp (zyy of run intialization
	Returns open file and results
	'''
	fn = ''
	fn = getlastmsg('filename', fn)
	
	out_file = open('../../data/'+fn+'.csv', "ab+", buffering=0)
	results = csv.writer(out_file, delimiter = ",")
	results.writerow(['Epoch time', 'Latitude', 'Longitude'] + sorted(list(sensor_dict))[:])
	return out_file, results

def write_data(results, epoch_time, lat, lon, sdict):
	'''
	Appends row to previously created log file 
	'''
	row = [epoch_time, lat, lon]
	for sensor in sorted(list(sdict)):
		row.append(sdict[sensor][2])
	results.writerow(row)

def close_file(out_file):
	'''
	Closes the log file
	'''
	out_file.close()
	sys.stdout.flush()

def initialize_gps():
	'''
	Initializes gps session
	'''
	session = gps.gps("localhost","2947")
	session.stream(gps.WATCH_ENABLE | gps.WATCH_NEWSTYLE)
	return session

def get_coordinates(session):
	'''
	Fetches coordinate data from gps
	'''
	try:
		report = session.next()
		#if report['class'] == "TPV":
		lat = getattr(report, 'lat', 0.0) #report.lat
		lon = getattr(report, 'lon', 0.0) #report.lon
		print("Success")
		return lat, lon
	except KeyError:
		print("KeyError")
		pass
	except KeyboardInterrupt:
		quit()
	except StopIteration:
		session = None
		print "Gpsd has terminated"

def get_time():
	'''
	Gets time delay from queue
	'''
	time_delay = 5 #Initialize to 5 seconds
	return int(getlastmsg('time', time_delay))

def open_and_resize_window():
	'''
	Opens and sizes the map
	'''
	os.system('xdg-open testmap.html')
	time.sleep(5)
	os.system('xdotool windowsize `xdotool search --onlyvisible --name firefox` 560 440')

def stop_systems(): #####################################################################################################################################
	'''
	Stop daqs
	'''
	stop_sensor('fromGUI_aq', 'Air Quality')
	stop_sensor('fromGUI_d3s', 'Radiation')
	stop_sensor('fromGUI_CO2', 'CO2')

def popuptext(sensor_dict, sensor_chosen):
	'''
	Formats popup texts
	'''
	popupv = ["Time: " + localtime() + '<br>'] # List for popup label (current time and values)
	
	for sensor in sorted(list(sensor_dict)): 
		if sensor==sensor_chosen:
			popupv.append(sensor+" (shown): ")
		else:
			popupv.append(sensor+": ")

		popupv.append(str(sensor_dict[sensor][2]) + "<br>")
			
	popuptext = ''.join(popupv) # Joins the list of popup labels into a string

def markercolor(sensor_dict, sensor):
	'''
	Fetches color of marker corresponding to the colorbar
	'''
	cmap = cm.get_cmap('spectral',sensor_dict[sensor][1]-sensor_dict[sensor][0])
	return matplotlib.colors.rgb2hex(cmap(int(sensor_dict[sensor][2]-sensor_dict[sensor][0]))[:3])

if __name__ == '__main__':
	try: # needed so that in the case of an error, it doesn't take a lot of work to kill loose processes
		#session = initialize_gps()
		sensor_array = ('Air Quality PM 2.5 (ug/m3)','CO2 (ppm)', 'Humidity (%)', 'Pressure (Pa)','Radiation (cps)', 'Temperature (C)')
		time_delay = get_time()
		sensor_dict = establish_dict(time_delay)
		out_file, results = create_file()
		
		location = folium.Map(location=[37.875830,-122.268459],zoom_start = 15) # Fetches chunk
		location.save('testmap.html')

		open_and_resize_window()
		for key in sensor_dict:
			
			sensor_dict[key].append(folium.FeatureGroup(name=key)) # Establishes Feature Groups
			makecolormap(key,sensor_dict[key][0],sensor_dict[key][1],'colormap'+key) # Creates Colormap that will be used as a legend
			sensor_dict[key][3].add_to(location) # Adds colormap to map
			cropcolorbar(('colormap'+key).replace(" ", "_").replace("/", "_")+'.png')

		folium.LayerControl().add_to(location)

		text = '' # Initializing text

		while True: # Starts collecting and plotting data
			text = getlastmsg('button', text)
			
			if text == 'stop':
				close_file(out_file)
				stop_systems()
				print("Stopped")
				break
			
			url = ('/home/pi/dosenet-raspberrypi/gps/colormap'+text.replace(" ", "_").replace("/", "_")+'.png')
			FloatImage(url, bottom = 5, left = 4).add_to(location) 
			
			lat, lon = uniform(37.875830,37.878), uniform(-122.268459,-122.278)
			
			# Uncomment the following block and delete the preceeding when it is time to incorporate actual gps data
			#lat, lon = get_coordinates(session)
			
			for key in sensor_dict:
				sensor_dict[key][2] = read_data(key)

			for key in sensor_dict:
				sensor_dict[key][3].show = (text == key)
				folium.Circle(radius = 20, location=[lat,lon], popup = popuptext(sensor_dict, key), fill_color = markercolor(sensor_dict, key),color = '#000000',fill_opacity = 1,stroke = 1,weight = 1).add_to(sensor_dict[key][3]) # Plot Circle
				location.save('testmap.html') # Saves map as html

			os.system('xdotool search "Mozilla Firefox" windowactivate --sync key --clearmodifiers ctrl+r') # Reloads the page
			write_data(results, time.time(), lat, lon, sensor_dict)
			time.sleep(time_delay)
	except:
		stop_systems()
		print("Something went wrong:")
		traceback.print_exc()

# Brought to you by big Al and Edward Lee
 
