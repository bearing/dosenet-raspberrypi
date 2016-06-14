from auxiliaries import datetime_from_epoch
from sender import ServerSender
from sensor import Sensor
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
		
	self.manager = manager
    def test_send(self, cpm, cpm_err):
        """
	Test Mode
	"""
	self.vprint(
	    1, ANSI_RED + " * Test mode, not sending to server * " +
	    ANSI_RESET)

    def no_config_send(self, cpm, cpm_err):
	"""
	Configuration file not present
	"""
	self.vprint(1, "Missing config file, not sending to server")

    def no_publickey_send(self, cpm, cpm_err):
    	"""
	Publickey not present
	"""
	self.vprint(1, "Missing public key, not sending to server")

    def no_network_send(self, cpm, cpm_err):
        """
	Network is not up
	"""
	self.vprint(1, "Network down, not sending to server")
	self.manager.send_to_queue(cpm, cpm_err)

    def regular_send(self, cpm, cpm_err):
        """
	Normal send
	"""
	try:
	    self.manager.sender.send_cpm(cpm, cpm_err)
	    if len(self.manager.queue) != 0:
	        for i in self.manager.queue:
	    	    self.manager.sender.send_cpm(cpm[i][1], cpm_err[i][2])
	except socket.error:    
	    self.manager.send_to_queue(cpm, cpm_err)

    def main(self, datalog, cpm, cpm_err, this_start, this_end, counts):
        """
    	Determines how to handle the cpm data.
    	"""
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
	
	self.manager.data_log(datalog, cpm, cpm_err)

	if self.manager.test:
	    self.test_send(cpm, cpm_err)
	elif not self.manager.config:
	    self.no_config_send(cpm, cpm_err)
	elif not self.manager.publickey:
	    self.no_publickey_send(cpm, cpm_err)
	elif not self.manager.network_up:
	    self.no_network_send(cpm, cpm_err)
	else:
	    self.regular_send(cpm, cpm_err)


