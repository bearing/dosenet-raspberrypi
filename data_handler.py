from auxiliaries import datetime_from_epoch
from sender import ServerSender
from sensor import Sensor
#from manager import Manager
from auxiliaries import set_verbosity
from globalvalues import ANSI_RESET, ANSI_YEL, ANSI_GR, ANSI_RED
from collections import deque
import socket
import time

CPM_DISPLAY_TEXT = (
    '{{time}}: {yellow} {{counts}} cts{reset}' +
    ' --- {green}{{cpm:.2f}} +/- {{cpm_err:.2f}} cpm{reset}' +
    ' ({{start_time}} to {{end_time}})').format(
    yellow=ANSI_YEL, reset=ANSI_RESET, green=ANSI_GR)
strf = '%H:%M:%S'

class Data_Handler(object):
	"""
	Object for sending data to server. 

	Also handles writing to datalog and 
	storing to memory. 
	"""

	def __init__(self,
		        manager=None,
		        verbosity=1,
		        logfile=None):

		self.v = verbosity
		if manager and logfile is None:
			set_verbosity(self, logfile=manager.logfile)
		else:
			set_verbosity(self, logfile=logfile)

	def test_send(self, datalog, cpm, cpm_err):
		"""
		Test Mode
		"""
		self.vprint(
			1, ANSI_RED + " * Test mode, not sending to server * " +
    		ANSI_RESET)
		manager.data_log(datalog, cpm, cpm_err)

	def no_config_send(self, datalog, cpm, cpm_err):
		"""
		Configuration file not present
		"""
		self.vprint(1, "Missing config file, not sending to server")
        	manager.data_log(datalog, cpm, cpm_err)

	def no_publickey_send(self, datalog, cpm, cpm_err):
    		"""
	    	Publickey not present
	    	"""
	    	self.vprint(1, "Missing public key, not sending to server")
	        manager.data_log(datalog, cpm, cpm_err)

    	def no_network_send(self, datalog, cpm, cpm_err):
	    	"""
	    	Network is not up
	    	"""
	    	self.vprint(1, "Network down, not sending to server")
	        manager.data_log(datalog, cpm, cpm_err)
	        manager.send_to_queue(cpm, cpm_err)

    	def regular_send(self, datalog, cpm, cpm_err):
	    	"""
	    	Normal send
	    	"""
	    	try:
	            manager.data_log(datalog, cpm, cpm_err)
	            manager.sender.send_cpm(cpm, cpm_err)
	        except socket.error:    
	            manager.send_to_queue(cpm, cpm_err)

    	def main(self, datalog, cpm, cpm_err, this_start, this_end, counts):
	    	#cpm, cpm_err = manager.sensor.get_cpm(manager.this_start, manager.this_end)
	    	#counts = int(round(cpm * manager.interval / 60))
	
	    	start_text = datetime_from_epoch(this_start).strftime(strf)
	    	end_text = datetime_from_epoch(this_end).strftime(strf)
	
	    	self.vprint(1, CPM_DISPLAY_TEXT.format(
	        	time=datetime_from_epoch(time.time()),
	        	counts=counts,
	        	cpm=cpm,
	        	cpm_err=cpm_err,
	        	start_time=start_text,
	       		end_time=end_text,
	    	))

	    	if manager.test:
	    		self.test_send(datalog, cpm, cpm_err)
	    	elif not manager.config:
	    		self.no_config_send(datalog, cpm, cpm_err)
	    	elif not manager.publickey:
	    		self.no_publickey_send(datalog, cpm, cpm_err)
	    	elif not manager.network_up:
	    		self.no_network_send(datalog, cpm, cpm_err)
	    	else:
	    		self.regular_send(datalog, cpm, cpm_err)


