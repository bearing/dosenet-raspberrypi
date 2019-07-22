import json
import sys
import pika

from PyQt5.QtWidgets import QMainWindow, QApplication, QPushButton, QWidget, QAction, QTabWidget,QVBoxLayout, QLabel, QCheckBox, QRadioButton, QComboBox
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import pyqtSlot

sensors = ('Air Quality PM 2.5 (ug/m3)','CO2 (ppm)', 'Humidity (%)', 'Pressure (Pa)','Radiation (cps)', 'Temperature (C)') # Tuple of Possible sensors -- Make sure this is in alphabetical order
selected_sensors = [] # List for selected sensors
started = False

def clear_queue(queue):
	'''
	Clears given queues.
	'''
	connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
	channel = connection.channel()
	channel.queue_declare(queue=queue)
	channel.queue_delete(queue=queue)
	connection.close()

class App(QMainWindow):

	def __init__(self):
		super().__init__()
		self.title = 'GUI'
		self.left = 0
		self.top = 0
		self.width = 300
		self.height = 200
		
		#self.layout = QFormLayout()
		
		self.initUI()
		
	def initUI(self):
		self.setWindowTitle(self.title)
		self.setGeometry(self.left, self.top, self.width, self.height)
		self.initLayout()
		
	def initLayout(self):
		self.setCentralWidget(MyTableWidget(self))
		
class MyTableWidget(QWidget):
	def __init__(self, parent):
		super(QWidget, self).__init__(parent)
		self.layout = QVBoxLayout(self)
		
		# Initialize tab screen
		self.tabs = QTabWidget()
		self.tab1 = QWidget()
		self.tabs.resize(300,200)
		
		# Add tabs
		self.tabs.addTab(self.tab1,"Sensor GUI")
		
		# Create first tab
		self.tab1.layout = QVBoxLayout(self)
		self.pushButton1 = QPushButton("PyQt5 button")
		self.tab1.layout.addWidget(checkdemo(sensors))
		self.tab1.setLayout(self.tab1.layout)
		
		# Add tabs to widget
		self.layout.addWidget(self.tabs)
		
		# Add start button to widget
		start = QPushButton('Start GPS GUI')
		start.setStyleSheet('QPushButton {background-color:#66B2FF}')
		start.clicked.connect(lambda:self.start_gps_GUI()) 
		self.tab1.layout.addWidget(start)
		
		# Add time delay to widget
		self.time_delay_dropdown = combodemo()
		self.tab1.layout.addWidget(self.time_delay_dropdown)
		
		self.setLayout(self.layout)
	
	def start_gps_GUI(self):
		#print(selected_sensors)
		self.tab2 = QWidget()
		self.tabs.addTab(self.tab2, "GPS GUI")
		
		self.tab2.layout = QVBoxLayout(self)
		self.possible_sensors = Radiodemo()
		self.tab2.layout.addWidget(self.possible_sensors)
		self.tab2.setLayout(self.tab2.layout)
		
		startSensors = QPushButton("Start Plotting")
		startSensors.setStyleSheet('QPushButton {background-color:#66B2FF}')
		startSensors.clicked.connect(lambda:self.start_mapping())
		
		self.tab2.layout.addWidget(startSensors)
	
	def start_mapping(self):
		global started
		if not started:
			global visualized_sensor
			self.sendmsg(json.dumps({'id':'Time Delay', 'cmd':self.time_delay_dropdown.time}), 'control')
			self.sendmsg(json.dumps({'id':'Sensors', 'cmd':selected_sensors}), 'control')
			self.sendmsg(json.dumps({'id':'Shown Sensor', 'cmd':self.possible_sensors.visualized_sensor}), 'control')
			started = True
		
		
	def sendmsg(self,s,queue):
		'''
		Sends a message through the selected queue.
		'''
		connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
		channel = connection.channel()

		channel.queue_declare(queue=queue)
		channel.basic_publish(exchange='', routing_key=queue, body=s)
		connection.close()
		
		
class Radiodemo(QWidget):
	def __init__(self, parent = None):
		super(Radiodemo, self).__init__(parent)
		
		layout = QVBoxLayout()
		
		layout.addWidget(QLabel("Sensor to plot:"))
		
		self.buttons = []
		
		for i in range(0, len(selected_sensors)):
			self.buttons.append(QRadioButton(selected_sensors[i]))
			self.buttons[i].toggled.connect(lambda:self.btnstate())
			layout.addWidget(self.buttons[i])
		
		self.buttons[0].setChecked(True)

		self.setLayout(layout)
		
	def btnstate(self):
		global started
		sensor = self.sender()
		if sensor.isChecked():
			if started:
				self.sendmsg(json.dumps({'id':'Shown Sensor', 'cmd':sensor.text()}), 'control')
			else:
				self.visualized_sensor = sensor.text()
			
	def sendmsg(self,s,queue):
		'''
		Sends a message through the selected queue.
		'''
		connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
		channel = connection.channel()

		channel.queue_declare(queue=queue)
		channel.basic_publish(exchange='', routing_key=queue, body=s)
		connection.close()
		
		
	
	

class checkdemo(QWidget):
	def __init__(self,sensors, parent = None):
		super(checkdemo, self).__init__(parent)

		layout = QVBoxLayout()
		
		
		self.buttons = [] # Initializes list of buttons

		
		layout.addWidget(QLabel('Possible Sensors:'))
		
		for i in range(0, len(sensors)): # Creates a button for every element in sensors and connects buttons to btnstate
			self.buttons.append(QCheckBox(sensors[i]))
			self.buttons[i].stateChanged.connect(lambda:self.add_to_list())
			layout.addWidget(self.buttons[i]) # Adds buttons to the layout
		
		self.setLayout(layout)

	def add_to_list(self): # Adds sensor name to list if it is checked, removes it if it is unchecked
		b = self.sender() 
		
		if b.isChecked():
			selected_sensors.append(b.text())
		if not b.isChecked():
			selected_sensors.remove(b.text())
		#print(selected_sensors)

class combodemo(QWidget):
	def __init__(self, parent = None):
		super(combodemo, self).__init__(parent)

		self.time = 5
		self.possible_times = ('5', '10', '15', '20', '25', '30', '35', '40', '45', '50', '55', '60')

		layout = QVBoxLayout()
		self.cb = QComboBox()
		for ptimes in self.possible_times:
			self.cb.addItem(ptimes + ' seconds')
			
		self.cb.currentIndexChanged.connect(lambda:self.selectionchange())
		
		layout.addWidget(QLabel("Time Delay:"))
		layout.addWidget(self.cb)
		
		self.setLayout(layout)

	def selectionchange(self):
		print (self.cb.currentText())
		self.time = int(self.cb.currentText().strip(' seconds'))
		

if __name__ == '__main__':
	clear_queue('control')
	clear_queue('to_GUI')
	clear_queue('from_GUI')
	
	app = QApplication(sys.argv)
	ex = App()
	ex.show()
	sys.exit(app.exec_())
