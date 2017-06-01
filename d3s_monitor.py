import fileinput
import os
import sys
            
log_phrase = 'total counts from'
found_phrase = False
for line in fileinput.input("/tmp/d3s_manager.log"):
    if log_phrase in line:
    	found_phrase = True

if found_phrase:
	sys.exit()
else:
	os.system('sudo reboot')
