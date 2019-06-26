import sys 
import os
import pika
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

selected_sensors = [] # List for selected sensors
sensors = ('Air Quality PM 2.5 (ug/m3)','CO2 (ppm)', 'Humidity (%)', 'Pressure (Pa)','Radiation (cps)', 'Temperature (C)') # Tuple of Possible sensors -- Make sure this is in alphabetical order

def create_sensor_GUI(time):
	'''
	Starts button.py and sends it the necessary information while sending mapplot.py the time delay that was selected
	'''
	
	sendmsg(time, 'time')
	
	if selected_sensors == []: # Checks at least one sensor is selected
		print("You haven't selected anything, silly.")
	else:
		selected_sensors.sort() # Sorts alphabetically
		sendmsg(','.join(selected_sensors),'master_button') # Sends list of selected_sensors as comma seperated string
		os.system('python3 button.py') # Runs secondary GUI 

def sendmsg(s,queue):
	'''
	Sends a message through the selected queue.
	'''
	connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
	channel = connection.channel()

	channel.queue_declare(queue=queue)
	channel.basic_publish(exchange='', routing_key=queue, body=str(s))
	connection.close()



class checkdemo(QWidget):
	def __init__(self, sensors, parent = None):
		super(checkdemo, self).__init__(parent)

		layout = QVBoxLayout()
		
		self.buttons = [] # Initializes list of buttons
		
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

class combodemo(QWidget):
	def __init__(self, parent = None):
		super(combodemo, self).__init__(parent)

		self.time = 5
		self.possible_times = ('5', '10', '15', '20', '25', '30', '35', '40', '45', '50', '55', '60')

		layout = QVBoxLayout()
		self.cb = QComboBox()
		for ptimes in self.possible_times:
			self.cb.addItem(ptimes)
			
		self.cb.currentIndexChanged.connect(lambda:self.selectionchange())
		
		layout.addWidget(QLabel("Time"))
		layout.addWidget(self.cb)
		
		self.setLayout(layout)
		self.setWindowTitle("combo box demo")

	def selectionchange(self):
		print (self.cb.currentText())
		self.time = int(self.cb.currentText())




if __name__ == '__main__': 
	
	app = QApplication(sys.argv)
	window = QWidget()
	
	start = QPushButton('Start')
	start.clicked.connect(lambda:create_sensor_GUI(dropdown.time)) 
	start.show()
	
	ex = checkdemo(sensors)
	
	dropdown = combodemo()
	
	# label = QLabel()
	# label.setPixmap(QPixmap('dosenet.png'))
	# label.resize(240, 88)
	
	layout = QVBoxLayout()
	layout.addWidget(start)
	layout.addWidget(ex)
	layout.addWidget(dropdown)
#	layout.addWidget(label)
	
	window.setLayout(layout)
	window.setWindowTitle("Sensor GUI")
	window.setGeometry(560, 20, 240, 440)
	window.show()
	
	sys.exit(app.exec_())

# Brought to you by big Al and Edward Lee
