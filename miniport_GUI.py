'''
	Author: Albert Qiang
	hit me up on facebook for that collab
'''
import json
import sys
import pika
import atexit
import os

from PyQt5.QtWidgets import QMainWindow, QApplication, QPushButton, QWidget, QTabWidget, QVBoxLayout, QHBoxLayout, \
	QLabel, QCheckBox, QRadioButton, QComboBox, QLineEdit, QFormLayout, QScrollArea, QGridLayout
from PyQt5.QtCore import Qt
from PyQt5.QtCore import QTimer
from PyQt5 import QtGui

display_sensor = ""



def get_last_message(ID):
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
				channel.basic_ack(delivery_tag=method_frame.delivery_tag)
			else:
				channel.basic_ack(delivery_tag=method_frame.delivery_tag)
	
	connection.close()
	
	return value
	
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
		self.left, self.top, self.width, self.height = 560, 20, 240, 440

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
		self.SensorDropDown = SensorDropDown(self.activeSensors)#############################################################################

		# Creates Text Display
		self.textDisplay = TextDisplayWindow(self.activeSensors) ##########################

		# Adds widgets to plottingWidget class
		self.layout = QVBoxLayout()
		self.layout.addWidget(self.SensorDropDown) ####################################################################################################
		self.layout.addWidget(self.textDisplay) #########################
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
		self.setLayout(self.layout)
		

	def selectionChanged(self):
		
		global display_sensor
		display_sensor = self.dropdown.currentText()
		#self.sendMessage(display_sensor,"START","fromGUI")
		print (display_sensor)#self.dropdown.currentText())
		
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
		# counter
		self.i = 0
		# add QLabel
		self.qLbl = QLabel('Not yet initialized')
		# make QTimer
		self.qTimer = QTimer()
		#
		self.start = QPushButton('Start Timer')
		self.stop = QPushButton('Kill Everything')
	
		self.start.clicked.connect(lambda: self.startTimer(activeSensors))
		self.stop.clicked.connect(lambda: self.kill(activeSensors))
		# set interval to 1 s
		self.qTimer.setInterval(2000) # 1000 ms = 1 s
		# connect timeout signal to signal handler
		self.qTimer.timeout.connect(lambda: self.getSensorValue(activeSensors))
		# start timer

		self.layout = QVBoxLayout()
		self.qLbl.setFont(QtGui.QFont("Times", 25, QtGui.QFont.Bold))
		self.layout.addWidget(self.qLbl)
		self.layout.addWidget(self.start)
		self.layout.addWidget(self.stop)
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
				os.system('python air_quality_DAQ.py -i 1 &')
				self.sendMessage("Air Quality","START","fromGUI")
				
			elif sensor == "CO2":
				print("CO2 DAQ activated")
				os.system('python adc_DAQ.py -i 1 &')
				self.sendMessage("CO2","START","fromGUI")
				
				
			elif sensor == "Radiation":
				print("Radiation DAQ activated")
				
			elif sensor == "Humidity" or "Temperature" or "Pressure":
				if not weather_activated:
					print("Weather DAQ activated")
				weather_activated = True
				
		self.qTimer.start()
		
		"""
		I really screwed the pooch on this one
		Everything in the getSensorValue method is endless trash
		I must be drunk
		
		"""

	def getSensorValue(self,activeSensors):
		
		global display_sensor # This is largely uncesscary, but I'm stupid 
		
		print(display_sensor+"baguette boy lives again")
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
				display_sensor_data = "AQ: "+str(display_sensor_data['data'][1][0])
			else: 
				display_sensor_data = "AQ: N/A "
		elif display_sensor == "CO2":
			if display_sensor_data is not None:
				display_sensor_data = str("CO2: "+str('%.3f'%display_sensor_data['data'][0]))
			else: 
				display_sensor_data = "CO2: N/A "
		elif display_sensor == "Radiation":
			'''
			insert formatting for Radiation here
			'''
		elif display_sensor == "Humidity" or "Temperature" or "Pressure":
			if not weather_activated:
				"""
				insert formatting for Weather here
				"""
			weather_activated = True
		
		print(display_sensor_data)
		print(display_sensor_data)
		self.qLbl.setTextFormat(0) # Set format so that qLabel doesn't have to guess what kind of string is passed in
		
		self.qLbl.setText(display_sensor_data)
		
		#### IMPORTANT 
		#### THE RECEIVE LAST MESSAGE METHOD REMOVES THINGS FROM THE QUEUE
		#### DO NOT TRY TO USE IT TWICE AND BELIEVE YOU WILL GET THE SAME THING
		#### IT MIGHT BE FINE WITH AIR QUALITY SINCE IT PUSHES SO MANY THINGS OUT SO QUICKLY, BUT CO2 WILL NOT WORK SINCE IT PUSHES TO THE QUEUE SLOWER
		#### MUCH MORE WORK NEEDS TO BE DONE
	




if __name__ == '__main__':
	app = QApplication(sys.argv)
	GUI = GUI()
	GUI.show()

	sys.exit(app.exec_())

# This code is filth of the highest degree
# Brought to you from the Friday afternoons of Big Al

