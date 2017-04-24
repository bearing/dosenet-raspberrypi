import fileinput
import os
import sys

log_phrase = 'total counts from'
for line in fileinput.input("d3s_manager.log"):
    if log_phrase in line:
    	os.system('sudo shutdown') 
    else:
    	os.system('sudo reboot')