import sys 
import os
import pika
import time
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

selected_sensors = [] # List for selected sensors
sensors = ('Air Quality PM 2.5 (ug/m3)','CO2 (ppm)', 'Humidity (%)', 'Pressure (Pa)','Radiation (cps)', 'Temperature (C)') # Tuple of Possible sensors -- Make sure this is in alphabetical order

def sendmsg(s,queue):
	'''
	Sends a message through the selected queue.
	'''
	connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
	channel = connection.channel()

	channel.queue_declare(queue=queue)
	channel.basic_publish(exchange='', routing_key=queue, body=str(s))
	connection.close()
def filenamechanged(text):
	start.fn = text

class startbutton(QWidget):
	def __init__(self, parent = None):
		super(startbutton, self).__init__(parent)
		
		layout = QVBoxLayout()
		
		start = QPushButton('Start GPS GUI')
		start.clicked.connect(lambda:self.create_sensor_GUI(dropdown.time)) 
		start.setStyleSheet('QPushButton {background-color:#66B2FF}')
		layout.addWidget(start)
		
		self.setLayout(layout)
		
		self.fn = ''
	
	def create_sensor_GUI(self,time_delay):
		'''
		Starts button.py and sends it the necessary information while sending mapplot.py the time delay that was selected
		'''
		if selected_sensors == []: # Checks at least one sensor is selected
			print("You haven't selected anything, silly.")
		else:
			selected_sensors.sort() # Sorts alphabetically
			if self.fn == '':
				self.fn = 'GPS_Data_'
				for sensor in selected_sensors:
					self.fn = self.fn + sensor[0]
				self.fn = self.fn + '_' + str(time.ctime(time.time()))
			sendmsg(self.fn, 'filename')
			sendmsg(time_delay, 'time')
			sendmsg(','.join(selected_sensors),'master_button') # Sends list of selected_sensors as comma seperated string
			os.system('python3 button.py') # Runs secondary GUI

class checkdemo(QWidget):
	def __init__(self, sensors, parent = None):
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
			print(selected_sensors)
	

class selectionbuttons(QWidget):
	def __init__(self, parent = None):
		super(selectionbuttons, self).__init__(parent)
		
		layout = QHBoxLayout()
		
		selectall = QPushButton('Select All')
		selectall.clicked.connect(lambda:self.selection(True)) 
		selectall.setStyleSheet('QPushButton {background-color:#93DB70}')
		layout.addWidget(selectall)
		
		deselectall = QPushButton('Deselect All')
		deselectall.clicked.connect(lambda:self.selection(False)) 
		deselectall.setStyleSheet('QPushButton {background-color:#FF6666}')
		layout.addWidget(deselectall)
		
		self.setLayout(layout)
		
	def selection(self, select):
		for button in ex.buttons:
			button.setChecked(select)

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
		self.setWindowTitle("combo box demo")

	def selectionchange(self):
		print (self.cb.currentText())
		self.time = int(self.cb.currentText().strip(' seconds'))




if __name__ == '__main__': 
	
	app = QApplication(sys.argv)
	window = QWidget()
	
	#start = QPushButton('Start GPS GUI')
	#start.clicked.connect(lambda:create_sensor_GUI(dropdown.time)) 
	#start.setStyleSheet('QPushButton {background-color:#66B2FF}')
	start = startbutton()
	
	ex = checkdemo(sensors)
	
	selectionbuttons = selectionbuttons()
	
	dropdown = combodemo()
	
	#label = QLabel()
	#label.setPixmap(QPixmap('dosenet.png'))
	
	filename = QLineEdit()
	filename.textChanged.connect(filenamechanged)
	
	layout = QFormLayout()
	layout.addRow(start)
	layout.addRow(ex)
	layout.addRow(selectionbuttons)
	layout.addRow(QLabel('File name:'), filename)
	layout.addRow(dropdown)
	#layout.addWidget(label)
	
	window.setLayout(layout)
	window.setWindowTitle("Sensor GUI")
	window.setGeometry(560, 20, 240, 440)
	window.show()
	
	sys.exit(app.exec_())

# Brought to you by big Al and Edward Lee
