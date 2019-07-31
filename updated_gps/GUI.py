import json
import sys
import pika
import atexit
import os

from PyQt5.QtWidgets import QMainWindow, QApplication, QPushButton, QWidget, QTabWidget, QVBoxLayout, QHBoxLayout, QLabel, QCheckBox, QRadioButton, QComboBox, QLineEdit, QFormLayout, QScrollArea
from PyQt5.QtCore import Qt

class GUI(QMainWindow):
	def __init__(self):
		super().__init__()
		
		# Initializes parameters
		self.title = 'GUI'
		self.left, self.top, self.width, self.height = 560, 20, 240, 440
		
		# Clears used queues
		self.clearQueue('control')
		self.clearQueue('fromGUI')
		self.clearQueue('toGUI')
		
		self.initUI() # Create UI
		self.initLayout() # Make layout
		
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
		
	def stopPlottingPoints(self):
		print("Sending message to stop (if not plotting, ignore).")
		self.sendMessage('EXIT', 'EXIT', 'control')
	
	def sendMessage(self,ID,cmd,queue):
		'''
		Sends a message through the selected queue with the given ID.
		'''
		connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
		channel = connection.channel()

		channel.queue_declare(queue=queue)
		channel.basic_publish(exchange='', routing_key=queue, body=json.dumps({'id':ID, 'cmd':cmd}))
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
		self.fileCreation = fileCreation(self)
		self.timeDelay = timeDelay(self)
		
		# Adds widgets to sensor GUI tab
		self.sensorGUI.layout = QVBoxLayout(self)
		self.sensorGUI.layout.addWidget(self.startGPSGUIButton)
		self.sensorGUI.layout.addWidget(self.sensorChecklistAndButtons)
		self.sensorGUI.layout.addWidget(self.fileCreation)
		self.sensorGUI.layout.addWidget(self.timeDelay)
		self.sensorGUI.setLayout(self.sensorGUI.layout)
		
		# Adds tabs to tabWidget class
		self.layout.addWidget(self.tabs)
		self.setLayout(self.layout)

	def startGPSGUIButton(self):
		self.startSensors = QPushButton("Start Plotting")
		self.startSensors.setStyleSheet('QPushButton {background-color:red;}')
		self.startSensors.clicked.connect(lambda:self.secondTab())
		return self.startSensors
	
	def secondTab(self):
		if self.sensorChecklistAndButtons.sensorChecklist.selectedSensors != []:
			print(self.sensorChecklistAndButtons.sensorChecklist.selectedSensors)
			# If GPS GUI tab is already made, deletes it
			if self.tabs.count() == 2:
				self.tabs.removeTab(1)
				
				self.clearQueue('control')
				self.clearQueue('fromGUI')
				self.clearQueue('toGUI')
				
				if self.plottingWidget.started:
					print("Sending message to stop.")
					self.plottingWidget.sendMessage('EXIT', 'EXIT', 'control')
					self.plottingWidget.started = False
			
			# Adds GPS GUI tab
			self.GPSGUI = QWidget()
			self.tabs.addTab(self.GPSGUI, 'GPS GUI')
			
			# Creates widget for GPS GUI tab
			self.plottingWidget = plottingWidget(self, sorted(self.sensorChecklistAndButtons.sensorChecklist.selectedSensors), self.timeDelay.time, self.fileCreation.filename)
			
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
		self.selectAll.setStyleSheet('QPushButton {background-color:#66B2FF}')
		self.selectAll.clicked.connect(lambda:self.selectAllBoxes(True))
		
		self.deselectAll = QPushButton("Deselect All")
		self.deselectAll.setStyleSheet('QPushButton {background-color:#66B2FF}')
		self.deselectAll.clicked.connect(lambda:self.selectAllBoxes(False))
		
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
		self.sensors = ('Air Quality PM 2.5 (ug/m3)','CO2 (ppm)', 'Humidity (%)', 'Pressure (Pa)','Radiation (cps)','Radiation Bi (cps)','Radiation K (cps)','Radiation Tl (cps)', 'Temperature (C)') # Make sure this is in alphabetical order
		self.checkButtons = []
		self.selectedSensors = []
		self.widget = QWidget()
		
		# Initializes layout
		self.layout = QVBoxLayout(self.widget)
		self.layout.setAlignment(Qt.AlignTop)
		
		# Creates checkButton list using names from sensor tuple and adds them to sensorChecklistAndButtons class
		for sensor in self.sensors:
			self.checkButtons.append(QCheckBox(sensor))
			self.checkButtons[-1].stateChanged.connect(lambda:self.addToGPSGUI())
			self.layout.addWidget(self.checkButtons[-1])
		
		# Finalizes widget
		self.setWidget(self.widget)
		self.setWidgetResizable(True)
		
	def addToGPSGUI(self):
		sensorChanged = self.sender()
		
		if sensorChanged.isChecked():
			self.selectedSensors.append(sensorChanged.text())
		if not sensorChanged.isChecked():
			self.selectedSensors.remove(sensorChanged.text())
		
class fileCreation(QWidget):
	def __init__(self, parent):
		super(fileCreation, self).__init__(parent)
		
		# Initializes filename
		self.filename = ''
		
		# Creates label
		self.fileLabel = QLabel('File name:')
		
		# Creates input box for filename
		self.filenameInput = QLineEdit()
		self.filenameInput.textChanged.connect(lambda:self.filenameChanged())
		
		# Adds widgets to fileCreation class
		self.layout = QHBoxLayout()
		self.layout.addWidget(self.fileLabel)
		self.layout.addWidget(self.filenameInput)
		self.setLayout(self.layout)
		
	def filenameChanged(self):
		self.filename = self.filenameInput.text()

class timeDelay(QWidget):
	def __init__(self, parent):
		super(timeDelay, self).__init__(parent)
		
		# Initializes time delay/tuple of possible time delays
		self.time = 5
		self.possibleTimeDelays = range(5, 65, 5)
		
		# Creates label
		self.timeLabel = QLabel('Time Delay: ')
		
		# Creates dropdown selection
		self.dropdown = QComboBox()
		for time in self.possibleTimeDelays:
			self.dropdown.addItem(str(time) + ' seconds')
		self.dropdown.currentIndexChanged.connect(lambda:self.selectionChanged())
		
		# Adds widgets to timeDelay class
		self.layout = QHBoxLayout()
		self.layout.addWidget(self.timeLabel)
		self.layout.addWidget(self.dropdown)
		self.setLayout(self.layout)
	
	def selectionChanged(self):
		self.time = int(self.dropdown.currentText().strip(' seconds'))

class plottingWidget(QWidget):
	def __init__(self, parent, activeSensors, timeDelay, filename):
		super(plottingWidget, self).__init__(parent)
		
		# Initializes list of active sensors/time delay/filename
		self.activeSensors = activeSensors
		self.timeDelay = timeDelay
		self.filename = filename
		
		# Creates start and stop plotting buttons
		self.startPlotting = QPushButton('Start Plotting')
		self.startPlotting.setStyleSheet('QPushButton {background-color:#66B2FF}')
		self.startPlotting.clicked.connect(lambda:self.startPlottingPoints())
		
		self.stopPlotting = QPushButton('Stop Plotting')
		self.stopPlotting.setStyleSheet('QPushButton {background-color:#66B2FF}')
		self.stopPlotting.clicked.connect(lambda:self.stopPlottingPoints())
		
		# Creates radio button
		self.sensorRadioButtons = sensorRadioButtons(self.activeSensors)
		
		# Adds widgets to plottingWidget class
		self.layout = QVBoxLayout()
		self.layout.addWidget(self.startPlotting)
		self.layout.addWidget(self.stopPlotting)
		self.layout.addWidget(self.sensorRadioButtons)
		self.setLayout(self.layout)
	
	def startPlottingPoints(self):
		if not self.sensorRadioButtons.started:
			print("Sending message to start.")
			self.sendMessage('Sensors', self.activeSensors, 'control')
			self.sendMessage('Time Delay', self.timeDelay, 'control')
			self.sendMessage('Filename', self.filename, 'control')
			self.sendMessage('Shown Sensor', self.sensorRadioButtons.selectedButton, 'control')
			os.system('python3 map_plot.py &')
			self.sensorRadioButtons.started = True
		elif self.sensorRadioButtons.started:
			print("Already sent message to start.")
		
	def stopPlottingPoints(self):
		if self.sensorRadioButtons.started:
			print("Sending message to stop.")
			self.sendMessage('EXIT', 'EXIT', 'control')
			self.sensorRadioButtons.started = False
		elif not self.sensorRadioButtons.started:
			print("Already sent message to stop.")
	
	def sendMessage(self,ID,cmd,queue):
		'''
		Sends a message through the selected queue with the given ID.
		'''
		connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
		channel = connection.channel()

		channel.queue_declare(queue=queue)
		channel.basic_publish(exchange='', routing_key=queue, body=json.dumps({'id':ID, 'cmd':cmd}))
		connection.close()

class sensorRadioButtons(QScrollArea):
	def __init__(self, activeSensors):
		super(sensorRadioButtons, self).__init__()
		
		# Initializes list of active sensors/list of radio buttons/started boolean/widget
		self.activeSensors = activeSensors
		self.radioButtons = []
		self.selectedButton = self.activeSensors[0]
		self.started = False
		self.widget = QWidget()
		
		# Initializes layout
		self.layout = QVBoxLayout(self.widget)
		self.layout.setAlignment(Qt.AlignTop)
		
		# Creates radio buttons
		for sensor in self.activeSensors:
			print(sensor)
			self.radioButtons.append(QRadioButton(sensor))
			self.radioButtons[-1].toggled.connect(lambda:self.changedRadio())
			self.layout.addWidget(self.radioButtons[-1])
		
		# Initializes first option as selected
		self.radioButtons[0].setChecked(True)
		
		# Finalizes widget
		self.setWidget(self.widget)
		self.setWidgetResizable(True)
		
	def changedRadio(self):
		self.sensor = self.sender()
		if self.sensor.isChecked():
			self.selectedButton = self.sensor.text()
			print(self.selectedButton)
			if self.started:
				self.sendMessage('Shown Sensor', self.selectedButton, 'control')
	
	def sendMessage(self,ID,cmd,queue):
		'''
		Sends a message through the selected queue with the given ID.
		'''
		connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
		channel = connection.channel()

		channel.queue_declare(queue=queue)
		channel.basic_publish(exchange='', routing_key=queue, body=json.dumps({'id':ID, 'cmd':cmd}))
		connection.close()

if __name__ == '__main__':
	app = QApplication(sys.argv)
	GUI = GUI()
	GUI.show()
	
	atexit.register(GUI.stopPlottingPoints)
	
	sys.exit(app.exec_())
