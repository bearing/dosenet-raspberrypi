import fileinput
import os
import sys

from auxiliaries import D3S_data_absence

if D3S_data_absence.claim:
    os.system('sudo reboot')
else:
	sys.exit()
