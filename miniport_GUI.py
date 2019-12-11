'''
	Author: Albert Qiang
	hit me up on LinkedIn for that collab
'''
import json
import sys
import pika
import atexit
import os
import time
import csv

from PyQt5.QtWidgets import QMainWindow, QApplication, QPushButton, QWidget, QTabWidget, QVBoxLayout, QHBoxLayout, \
	QLabel, QCheckBox, QRadioButton, QComboBox, QLineEdit, QFormLayout, QScrollArea, QGridLayout
from PyQt5.QtCore import Qt
from PyQt5.QtCore import QTimer
from PyQt5 import QtGui

display_sensor = ""

row = {}


def get_last_message(ID):
	
	global row
	
	connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
	channel = connection.channel()
	channel.queue_declare(queue='toGUI')
	value = None
	method_frame, header_frame, body = channel.basic_get(queue='toGUI')
	
	while body != None:
		method_frame, header_frame, body = channel.basic_get(queue='toGUI')
		if body is not None:
			message = json.loads(body.decode('utf-8'))
			if message['id'] == ID:
				value = message
				row[ID] = value
				channel.basic_ack(delivery_tag=method_frame.delivery_tag)
			else:
				row[message['id']] = message
				channel.basic_ack(delivery_tag=method_frame.delivery_tag)
	
	connection.close()
	
	return value
	
def write_labels(filename):
	log_out_file = open(filename+'.csv', "a+")
	log_results = csv.writer(log_out_file, delimiter = ",")
	
	labels = ['Epoch Time','Air Quality','CO2','GPS','Humidity','Pressure','Radiation','Temperature']
	
	log_results.writerow(labels)
	
	log_out_file.close()
	
def write_data(filename,data_dictionary):
	
	log_out_file = open(filename+'.csv', "a+")
	log_results = csv.writer(log_out_file, delimiter = ",")
	
	file_row = [None] * 8
	
	"""
	Each label corresponds to an index based on its position in the labels array
	"""
	
	file_row[0]=(time.time())
	
	for sensor in data_dictionary:
		if sensor == "Air Quality":
			file_row[1]=((data_dictionary['Air Quality'])['data'][1][0])
		elif sensor == "CO2":
			file_row[2]=((data_dictionary['CO2'])['data'][0])
	
	
	log_results.writerow(file_row)
	
	log_out_file.close()
	
def clearQueue(queue):
	'''
	Clears given queue.
	'''
	connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
	channel = connection.channel()
	channel.queue_declare(queue=queue)
	channel.queue_delete(queue=queue)
	connection.close()
	

class GUI(QMainWindow):
	def __init__(self):
		super().__init__()

		# Initializes parameters
		self.title = 'GUI'
		self.left, self.top, self.width, self.height = 1, 30, 620, 450

		# Clears used queues
		#self.clearQueue('control')
		self.clearQueue('fromGUI')
		self.clearQueue('toGUI')

		self.initUI()  # Create UI
		self.initLayout()  # Make layout

	def initUI(self):
		self.setWindowTitle(self.title)
		self.setGeometry(self.left, self.top, self.width, self.height)

	def initLayout(self):
		self.tabWidget = tabWidget(self)
		self.setCentralWidget(self.tabWidget)

	def clearQueue(self, queue):
		'''
		Clears given queue.
		'''
		connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
		channel = connection.channel()
		channel.queue_declare(queue=queue)
		channel.queue_delete(queue=queue)
		connection.close()

	def sendMessage(self, ID, cmd, queue):
		'''
		Sends a message through the selected queue with the given ID.
		'''
		connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
		channel = connection.channel()

		channel.queue_declare(queue=queue)
		channel.basic_publish(exchange='', routing_key=queue, body=json.dumps({'id': ID, 'cmd': cmd}))
		connection.close()


class tabWidget(QWidget):
	def __init__(self, parent):
		super(QWidget, self).__init__(parent)

		# Sets vertical layout
		self.layout = QVBoxLayout(self)

		# Initializes tab screen
		self.tabs = QTabWidget()

		# Adds sensor GUI tab
		self.sensorGUI = QWidget()
		self.tabs.addTab(self.sensorGUI, 'Sensor GUI')

		# Creates widgets for sensor GUI tab
		self.startGPSGUIButton = self.startGPSGUIButton()
		self.sensorChecklistAndButtons = sensorChecklistAndButtons(self)
		self.sensorChecklistAndButtons.setStyleSheet("QScrollBar:vertical { width: 50px; }")
		

		# Adds widgets to sensor GUI tab
		self.sensorGUI.layout = QVBoxLayout(self)
		self.sensorGUI.layout.addWidget(self.startGPSGUIButton)
		self.sensorGUI.layout.addWidget(self.sensorChecklistAndButtons)
		self.sensorGUI.setLayout(self.sensorGUI.layout)

		# Adds tabs to tabWidget class
		self.layout.addWidget(self.tabs)
		self.setLayout(self.layout)

	def startGPSGUIButton(self):
		self.startSensors = QPushButton("Start Plotting")
		self.startSensors.clicked.connect(lambda: self.secondTab())
		return self.startSensors

	def secondTab(self):
		if self.sensorChecklistAndButtons.sensorChecklist.selectedSensors != []:
			# If GPS GUI tab is already made, deletes it
			if self.tabs.count() == 2:
				self.tabs.removeTab(1)

				#self.clearQueue('control')
				self.clearQueue('fromGUI')
				self.clearQueue('toGUI')

				#if self.plottingWidget.sensorRadioButtons.started:
				#    print("Sending message to stop.")
				#    self.plottingWidget.sendMessage('EXIT', 'EXIT', 'control')
				#    self.plottingWidget.started = False

			# Adds GPS GUI tab
			self.GPSGUI = QWidget()
			self.tabs.addTab(self.GPSGUI, 'Display')

			# Creates widget for GPS GUI tab
			self.plottingWidget = plottingWidget(self, sorted(self.sensorChecklistAndButtons.sensorChecklist.selectedSensors))

			# Adds widget to GPS GUI tab
			self.GPSGUI.layout = QVBoxLayout()
			self.GPSGUI.layout.addWidget(self.plottingWidget)
			self.GPSGUI.setLayout(self.GPSGUI.layout)

			# Shifts focus to GPS GUI tab
			self.tabs.setCurrentIndex(1)
		else:
			print("You didn't select any sensors.")

	def clearQueue(self, queue):
		'''
		Clears given queue.
		'''
		connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
		channel = connection.channel()
		channel.queue_declare(queue=queue)
		channel.queue_delete(queue=queue)
		connection.close()


class sensorChecklistAndButtons(QWidget):
	def __init__(self, parent):
		super(sensorChecklistAndButtons, self).__init__(parent)

		# Creates label
		self.checklistLabel = QLabel('Possible Sensors:')

		# Creates checklist
		self.sensorChecklist = sensorChecklist()

		# Creates select all and deselect all buttons
		self.selectAll = QPushButton("Select All")
		self.selectAll.clicked.connect(lambda: self.selectAllBoxes(True))

		self.deselectAll = QPushButton("Deselect All")

		self.deselectAll.clicked.connect(lambda: self.selectAllBoxes(False))

		# Adds widgets to sensorChecklistAndButtons class
		self.layout = QFormLayout()
		self.layout.addRow(self.checklistLabel)
		self.layout.addRow(self.sensorChecklist)
		self.layout.addRow(self.selectAll, self.deselectAll)
		self.setLayout(self.layout)

	def selectAllBoxes(self, select):
		for button in self.sensorChecklist.checkButtons:
			button.setChecked(select)


class sensorChecklist(QScrollArea):
	def __init__(self):
		super(sensorChecklist, self).__init__()

		# Initializes tuple of sensors/list of check buttons/list of selected sensors
		self.sensors = ('Air Quality', 'CO2', 'Humidity', 'Pressure', 'Radiation',
						'Temperature')  # Make sure this is in alphabetical order
		self.checkButtons = []
		self.selectedSensors = []
		self.widget = QWidget()

		# Initializes layout
		self.layout = QVBoxLayout(self.widget)
		self.layout.setAlignment(Qt.AlignTop)

		# Creates checkButton list using names from sensor tuple and adds them to sensorChecklistAndButtons class
		for sensor in self.sensors:
			self.checkButtons.append(QCheckBox(sensor))
			self.checkButtons[-1].stateChanged.connect(lambda: self.addToGPSGUI())
			self.layout.addWidget(self.checkButtons[-1])
		
		print(self.checkButtons)

		# Finalizes widget
		self.setWidget(self.widget)
		self.setWidgetResizable(True)

	def addToGPSGUI(self):
		sensorChanged = self.sender()

		if sensorChanged.isChecked():
			self.selectedSensors.append(sensorChanged.text())
		if not sensorChanged.isChecked():
			self.selectedSensors.remove(sensorChanged.text())


class plottingWidget(QWidget):
	def __init__(self, parent, activeSensors):
		super(plottingWidget, self).__init__(parent)

		# Initializes list of active sensors/time delay/filename
		self.activeSensors = activeSensors

		# Creates Dropdown Menu
		self.SensorDropDown = SensorDropDown(self.activeSensors)

		# Creates Text Display
		self.textDisplay = TextDisplayWindow(self.activeSensors) 

		# Start/Stop buttons
		buttonWidget = QWidget()
		self.start = QPushButton('Start')
		self.stop = QPushButton('Stop')
	
		# make QTimer
		self.qTimer = QTimer()
		# set interval to 1 s
		self.qTimer.setInterval(2000) # 1000 ms = 1 s
		# connect timeout signal to signal handler
		self.qTimer.timeout.connect(lambda: self.getSensorValue(activeSensors,self.file_header))
		# start timer

		self.start.clicked.connect(lambda: self.startTimer(self.activeSensors))
		self.stop.clicked.connect(lambda: self.kill(self.activeSensors))
		button_layout = QHBoxLayout()
		button_layout.addWidget(self.start)
		button_layout.addWidget(self.stop)
		buttonWidget.setLayout(button_layout)

		# Adds widgets to plottingWidget class
		self.layout = QVBoxLayout()
		self.layout.addWidget(self.SensorDropDown,2) 
		self.layout.addWidget(self.textDisplay,6)
		self.layout.addWidget(buttonWidget,2)
		self.setLayout(self.layout)

	def sendMessage(self, ID, cmd, queue):
		'''
		Sends a message through the selected queue with the given ID.
		'''
		connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
		channel = connection.channel()

		channel.queue_declare(queue=queue)
		channel.basic_publish(exchange='', routing_key=queue, body=json.dumps({'id': ID, 'cmd': cmd}))
		connection.close()

	def kill(self,activeSensors):
		for i in activeSensors:
			self.sendMessage(i,"EXIT","fromGUI")
		sys.exit()

	def startTimer(self,activeSensors):
		
		weather_activated = False

		for sensor in activeSensors:

			if sensor == "Air Quality":
				print("Air Quality DAQ activated")
				os.system('python3 /home/pi/dosenet-raspberrypi/air_quality_DAQ.py -i 1 &')
				self.sendMessage("Air Quality","START","fromGUI")
				
			elif sensor == "CO2":
				print("CO2 DAQ activated")
				os.system('python3 /home/pi/dosenet-raspberrypi/adc_DAQ.py -i 1 &')
				self.sendMessage("CO2","START","fromGUI")

			elif sensor == "Radiation":
				print("Radiation DAQ activated")
				os.system('python3 /home/pi/dosenet-raspberrypi/pocket_geiger_DAQ.py -i 1 &')
				self.sendMessage("Radiation","START","fromGUI")
				
			elif sensor == "Humidity" or "Temperature" or "Pressure":
				if not weather_activated:
					print("Weather DAQ activated")
					os.system('python3 /home/pi/dosenet-raspberrypi/weather_DAQ_rabbitmq.py -i 1 &')
					self.sendMessage("Weather","START","fromGUI")
				weather_activated = True
				
		self.qTimer.start()
	
	def getSensorValue(self,activeSensors,log_file_name):
		
		global display_sensor # I'm not sure this is necessary
		
		print(display_sensor+" baguette boy lives again") # damn right he does
		print("________________________________________________________________") #str(receive_last_message(ID = "CO2",queue="toGUI",message="")))
		default_id = activeSensors[0]
		
		if display_sensor == "":
			display_sensor = default_id
			print(display_sensor)
		
		display_sensor_data = json.dumps((get_last_message(ID=display_sensor)))
		print(display_sensor_data)
		display_sensor_data = (json.loads(display_sensor_data))
		
		
		
		if display_sensor == "Air Quality":
			if display_sensor_data is not None:
				display_sensor_data = "PM2.5: "+str(display_sensor_data['data'][1][0]+" μg/L")
			else: 
				display_sensor_data = "AQ: N/A "
		elif display_sensor == "CO2":
			if display_sensor_data is not None:
				display_sensor_data = str("CO2: "+str('%.1f'%display_sensor_data['data'][0])+" ppm")
			else: 
				display_sensor_data = "CO2: N/A "
		elif display_sensor == "Radiation":
			if display_sensor_data is not None:
				display_sensor_data = str("μSv/hr: "+str('%.3f'%(display_sensor_data['data'][0]*0.036)))
			else: 
				display_sensor_data = "CPM: N/A "
		elif display_sensor == "Humidity":
			if display_sensor_data is not None:
				display_sensor_data = str("% H: "+str('%.1f'%display_sensor_data['data'][0]))
			else: 
				display_sensor_data = "% Humidity: N/A "
		elif display_sensor == "Temperature":
			if display_sensor_data is not None:
				display_sensor_data = str("T: "+str('%.1f'%display_sensor_data['data'][0])+" C")
			else: 
				display_sensor_data = "Temp: N/A "
		elif display_sensor == "Pressure":
			if display_sensor_data is not None:
				display_sensor_data = str("P: "+str('%.4f'%display_sensor_data['data'][0])+" atm")
			else: 
				display_sensor_data = "Pressure: N/A "
		
		print(display_sensor_data)
		print(display_sensor_data)
		print(str(row)+"**************************************")
		
		write_data(log_file_name,row)
		
		self.qLbl.setTextFormat(0) # Set format so that qLabel doesn't have to guess what kind of string is passed in
		
		self.qLbl.setText(display_sensor_data)
	
	"""
	
	♪♪♬♪ endless trash ♬♪♪♪
	
	"""


class SensorDropDown(QWidget):
	def __init__(self, activeSensors):
		super(SensorDropDown, self).__init__()

		self.activeSensors = activeSensors
		print (self.activeSensors)
		# Creates label
		self.sensorLabel = QLabel('Sensors')

		# Creates dropdown selection
		self.dropdown = QComboBox()
		for sensor in self.activeSensors:
			self.dropdown.addItem(str(sensor))
		self.dropdown.currentIndexChanged.connect(lambda: self.selectionChanged())

		# Adds widgets to timeDelay class
		self.layout = QHBoxLayout()
		self.layout.addWidget(self.sensorLabel)
		self.layout.addWidget(self.dropdown)
		self.layout.setAlignment(Qt.AlignTop)
		self.setLayout(self.layout)
		

	def selectionChanged(self):
		
		global display_sensor
		display_sensor = self.dropdown.currentText()
		print (display_sensor)
		
	def sendMessage(self, ID, cmd, queue):
		'''
		Sends a message through the selected queue with the given ID.
		'''
		connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
		channel = connection.channel()

		channel.queue_declare(queue=queue)
		channel.basic_publish(exchange='', routing_key=queue, body=json.dumps({'id': ID, 'cmd': cmd}))
		connection.close()


class TextDisplayWindow(QWidget):
	# constructor
	def __init__(self,activeSensors):
		super(TextDisplayWindow, self).__init__()
		print(activeSensors)
		
		self.file_header = time.strftime('GUI_Data_%Y-%m-%d_%H:%M:%S_', time.localtime()) # name of the file
		write_labels(self.file_header)
		
		# counter
		self.i = 0
		# add QLabel
		self.qLbl = QLabel('Not yet initialized')

		self.layout = QVBoxLayout()
		self.qLbl.setFont(QtGui.QFont("Times", 38, QtGui.QFont.Bold))
		self.qLbl.setAlignment(Qt.AlignCenter)
		self.layout.addWidget(self.qLbl)
		#self.layout.addWidget(self.start)
		#self.layout.addWidget(self.stop)
		self.setLayout(self.layout)
	
	
		
	
	def sendMessage(self, ID, cmd, queue):
		'''
		Sends a message through the selected queue with the given ID.
		'''
		connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
		channel = connection.channel()

		channel.queue_declare(queue=queue)
		channel.basic_publish(exchange='', routing_key=queue, body=json.dumps({'id': ID, 'cmd': cmd}))
		connection.close()




if __name__ == '__main__':
	app = QApplication(sys.argv)
	app.setFont(QtGui.QFont("Times", 22))
	GUI = GUI()
	GUI.show()

	sys.exit(app.exec_())

# Brought to you by Big Al's Friday afternoons

