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

#session = gps.gps("localhost","2947")
#session.stream(gps.WATCH_ENABLE | gps.WATCH_NEWSTYLE) Uncomment this when you want to actually start collecting gps data

print("mapplot.py is up and running :) ")

####################################################################################################################################### Change and add labels here (alphabetical order)
sensor_array = ('Air Quality PM 2.5 (ug/m3)','CO2 (ppm)', 'Humidity (%)', 'Pressure (Pa)','Radiation (cps)', 'Temperature (C)')



def clear_queue(queue):
	'''
	Clears 'toGUI' and 'fromGUI' queues.
	'''
	print("Initializing queues... clearing out old data")
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
	
	temp = getlastmsg(queue, data)
	
	print(temp)
	
	if not temp:
		print("It's empty!")
	
	data = json.loads(temp)
	
	print data
	
	print(data) # Edit this to format data from each new sensor added from queue
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
	
	sendmsg(json.dumps({'id':sensor, 'cmd': "EXIT"}), queue)
	
def establish_dict(time_delay):
	'''
	Establishes the dictionary with all the sensor information. Add code here to add a new sensor.
	'''
	
	body = ''
	
	body = str(getlastmsg('sensor_list', body))

	sensors = str(body).split(',')
	
	sensor_dict = {}
	
######################################################################################################################################## Add code here for new sensor
	if sensor_array[0] in sensors:
		sensor_dict[sensor_array[0]] = [0, 100, 0] # Air Quality
		os.system('python aq_daq.py -i ' + str(time_delay) + ' &')
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
		
	time.sleep(time_delay) # Letting aq_daq.py boot up
	return sensor_dict
	# {'temp': [15, 30, 'Temperature', 0], 'pres': [99500, 101400, 'Pressure', 0], 'humi': [30, 60, 'Humidity', 0]} # Dictionary of minimum and maximum values for sensors

def makecolormap(label,minvalue,maxvalue,filename):
	'''
	Makes a color map with given maximum and minimum values.
	'''
	fig, ax = plt.subplots(figsize=(3,1))
	fig.subplots_adjust(bottom=0.5)

	cmap = mpl.cm.spectral

	norm = mpl.colors.Normalize(vmin=minvalue, vmax=maxvalue)

	
	cb1 = mpl.colorbar.ColorbarBase(ax, cmap=cmap,
								norm=norm,
								orientation='horizontal')
	cb1.set_label(label)
	
	filename = (filename.replace(" ", "_").replace("/", "_")+'.png')
	
	
	fig.savefig(filename)

def twodigits(num):
	if len(str(num)) == 1:
		return "0" + str(num)
	return str(num)

def localtime():
	current_time = time.localtime(time.time())
	days_of_the_week = ['Monday', 'Tuesday', 'It is Wednesday my dudes', 'Thursday', 'Friday', 'Saturday', 'Sunday']
	months = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
	return days_of_the_week[current_time.tm_wday-1] + ' ' + months[current_time.tm_mon-1] + ' ' + str(current_time.tm_mday) + ', ' + str(current_time.tm_year) + ' @ ' + twodigits(current_time.tm_hour) + ':' + twodigits(current_time.tm_min) + ':' + twodigits(current_time.tm_sec)

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
	print("In getlastmsg()")
	while True:
		print("In the While loop")
		body = getmsg(queue)
		if str(body) == 'None':
			print("In the if statement")
			break
		print("Setting text=body")
		text=str(body)
	print("Returning text as: " + text)
	return text

time_delay = 5
time_delay = int(getlastmsg('time', time_delay))

sensor_dict = establish_dict(time_delay)

location = folium.Map(location=[37.875830,-122.268459],zoom_start = 15) # Fetches chunk
location.save('testmap.html')

os.system('xdg-open testmap.html')
time.sleep(5)
os.system('xdotool windowsize `xdotool search --onlyvisible --name firefox` 560 440')


for key in sensor_dict:
	
	sensor_dict[key].append(folium.FeatureGroup(name=key)) # Establishes Feature Groups
	
	makecolormap(key,sensor_dict[key][0],sensor_dict[key][1],'colormap'+key) # Creates Colormap that will be used as a legend
	
	print('colormap'+key)
	
	sensor_dict[key][3].add_to(location) # Adds colormap to map


folium.LayerControl().add_to(location)

text = '' # Initializing text


while True: # Starts collecting and plotting data
	
	# Gets most recent command and sets the value of text equal to it
	
	text = getlastmsg('button', text)
	
	#####################################################################################################################################
	if text == 'stop':
		stop_sensor('fromGUI_aq', 'Air Quality')
		stop_sensor('fromGUI_d3s', 'Radiation')
		stop_sensor('fromGUI_CO2', 'CO2')
		
		print("Stopped")
		sys.exit(0)
	
	value = text
	value = value.replace(" ", "_").replace("/", "_")
	
	url = ('/home/pi/dosenet-raspberrypi/gps/colormap'+str(value)+'.png')
	FloatImage(url, bottom = 5, left = 30).add_to(location) 
	
	lat = uniform(37.875830,37.878)
	lon = uniform(-122.268459,-122.278)
	
	# Uncomment the following block and delete the preceeding when it is time to incorporate actual gps data
	
	# try:
		# report = session.next()
		# if report['class'] == "TPV":
			# lat = report.lat
			# lon = report.lon
	# except KeyError:
		# pass
	# except KeyboardInterrupt:
		# quit()
	# except StopIteration:
		# session = None
		# print "Gpsd has terminated"
	
	print(""" 
 (         )   (            )               
 )\ )   ( /(   )\ )      ( /(        *   )  
(()/(   )\()) (()/( (    )\()) (   ` )  /(  
 /(_)) ((_)\   /(_)))\  ((_)\  )\   ( )(_)) 
(_))_    ((_) (_)) ((_)  _((_)((_) (_(_())  
 |   \  / _ \ / __|| __|| \| || __||_   _|  
 | |) || (_) |\__ \| _| |  ` || _|   | |    
 |___/  \___/ |___/|___||_|\_||___|  |_|                          
	""")
	
	
	for key in sensor_dict:
		sensor_dict[key][2] = read_data(key)

	for key in sensor_dict:
		sensor_dict[key][3].show = (text == key)
		
		popupv = ["Time: " + localtime() + '<br>'] # List for popup label (current time and values)
		
		for i in sorted(list(sensor_dict)): 
			if i==key:
				popupv.append(i+" (shown): ")
			else:
				popupv.append(i+": ")

			popupv.append(str(sensor_dict[i][2]) + "<br>")
				
		popuptext = ''.join(popupv) # Joins the list of popup labels into a string
		
		cmap = cm.get_cmap('spectral',sensor_dict[key][1]-sensor_dict[key][0])
		
		markercolor = (matplotlib.colors.rgb2hex(cmap(int(sensor_dict[key][2]-sensor_dict[key][0]))[:3]))
		
		folium.Circle(radius = 20, location=[lat,lon], popup = popuptext, fill_color = markercolor,color = '#000000',fill_opacity = 1,stroke = 1,weight = 1).add_to(sensor_dict[key][3]) # Plot Circle
		
		location.save('testmap.html') # Saves map as html

	os.system('xdotool search "Mozilla Firefox" windowactivate --sync key --clearmodifiers ctrl+r') # Reloads the page
	
	time.sleep(time_delay)
	
# Brought to you by big Al and Edward Lee
 
