# Author: Yaro Kaminskiy

'''
This script securely copies the Pi-hat network configuration file from the Dosenet servers to a Pi-hat at a school of interest and
updates the network ID on the network configuration file for the Pi-hat.
'''

# Import the relevant modules and functions from the appropriate libraries for convenience.
import fileinput
import sys
import os

'''
Part 1: Securely copying the network configuration file from the Dosenet servers to the Pi-hat.
'''

# Ask the user for the csv file name and output the raw input string as a variable.
NAME = raw_input('What is the csv file name?: ')

# Print the csv file name inputed by the user for debugging purposes.
print 'FOR DEGUBBING, csv file name: %s' % NAME

# Define the paths to the source and target .csv files as arguments for the scp linux command to be executed through the os.sytem function.
sourcePath = 'dosenet@dosenet.dhcp.lbl.gov:~/config-files/' + NAME
targetPath = '/home/pi/config/config.csv'

# Execute the linux command line to securely copy the file over the Internet.
p = os.system('sudo scp "%s" "%s"' % (sourcePath, targetPath))

# Print the scp linux command that was executed for debugging purposes.
print 'FOR DEBUGGING, linux command: %s' % p

'''
Part 2: Updating the dosimeter ID on the network configuration file on the Pi-hat once it has been copied securely over the Internet.
'''

# Ask for the station ID and output the raw input string as a variable.
ID = raw_input('What is the station ID?: ')

'''
Loop through each line of the interfaces file to find the default station ID placeholder and replace it with the station ID provided
by the user.
'''
for line in fileinput.input('/etc/network/interfaces'):
    # Search and find 'wireless-essid' to indicate the place in the code to replace the default Pi-hat ID with the actual station's ID.
    if 'wireless-essid' in line:
        # Create a handle for a new line with the updated station ID to input into the interfaces file.      
        line = '  wireless-essid RPiAdHocNetwork' + ID + '\n'
    
    # Write the new line with the updated station ID in the interfaces file.
    sys.stdout.write(line)
