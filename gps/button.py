import sys
import os
import pika
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

running = [False] # sets running state to False as default

def sendmsg(s,queue):
	'''
	Sends a message through the selected queue.
	'''
	connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
	channel = connection.channel()

	channel.queue_declare(queue=queue)
	channel.basic_publish(exchange='', routing_key=queue, body=str(s))
	connection.close()

def start_gps():
	'''
	Starts 'mapplot.py'.
	'''
	if running[0]:
		print("Already starting")
	elif not running[0]:
		print("Starting")
		running[0] = True
		os.system('python mapplot.py &')
	else:
		print("How is this even possible") # funny
	

def stop_gps():
	'''
	Stops 'mapplot.py'.
	'''
	if running[0]:
		print("Stopping")
		running[0] = False
		connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
		channel = connection.channel()

		channel.queue_declare(queue='button')
		channel.basic_publish(exchange='', routing_key='button', body='stop')
		channel.basic_ack(multiple=True)
		connection.close()
	elif not running[0]:
		print("Already stopping")
	else:
		print("How is this even possible") # funny
		
def getmsg():
	'''
	Gets list of selected sensors from master button.
	'''
	connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost')) 
	channel = connection.channel()
	channel.queue_declare(queue='master_button')
	body = str(channel.basic_get(queue='master_button', auto_ack=True)[2])[2:-1]
	
	sendmsg(body, 'sensor_list')
	
	return str(body).split(',')
	
class Radiodemo(QWidget):
	def __init__(self, sensors, parent = None):
		super(Radiodemo, self).__init__(parent)
		
		layout = QVBoxLayout()
		
		layout.addWidget(QLabel("Sensor to plot:"))
		
		self.buttons = []
		
		for i in range(0, len(sensors)):
			self.buttons.append(QRadioButton(sensors[i]))
			self.buttons[i].toggled.connect(lambda:self.btnstate())
			layout.addWidget(self.buttons[i])
		
		self.buttons[0].setChecked(True)

		
		self.setLayout(layout)
		
	def btnstate(self):
		b = self.sender()
		if b.isChecked():
			sendmsg(b.text(), 'button')



def main():
	app = QApplication(sys.argv)
	window = QWidget()
   
	start = QPushButton('Start Plotting')
	start.clicked.connect(start_gps)
	start.setStyleSheet('QPushButton {background-color:#66B2FF}')
	stop = QPushButton('Stop Plotting')
	stop.clicked.connect(stop_gps)
	stop.setStyleSheet('QPushButton {background-color:#FF6666}')
	ex = Radiodemo(getmsg())
	label = QLabel()
	label.setPixmap(QPixmap('dosenet.png'))
	
	layout = QVBoxLayout()
	layout.addWidget(start)
	layout.addWidget(stop)
	layout.addWidget(ex)
	layout.addWidget(label)
	
	window.setLayout(layout)
	window.setWindowTitle("GPS GUI")
	window.setGeometry(560, 20, 240, 440)
	window.show()
	
	sys.exit(app.exec_())
	
if __name__ == '__main__':
	main()
	
# Brought to you by big Al and Edward Lee
