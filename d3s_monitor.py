import fileinput
import os
import sys
            
log_phrase = 'total counts from'
for line in fileinput.input("/tmp/d3s_manager.log"):
    if log_phrase in line:
    	sys.exit()
    else:
    	os.system('sudo reboot')
