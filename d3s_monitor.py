import fileinput
import os
import sys

from auxiliaries import d3s_data_absence

if d3s_data_absence.claim:
    os.system('sudo reboot')
else:
	sys.exit()
