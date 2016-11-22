# Author: Yaro Kaminskiy

# Use the built-in subprocess module and Popen function to securely copy the Pi-hat network configuration file from the Dosenet servers
# to a Pi-hat at a school of interest and to update the network ID on the network configuration file for a Pi-hat using a search algorithm.

'''
Part 1: Securely copying the network configuration file from the Dosenet servers to the Pi-hat.
'''

# Import the relevant modules and functions from the appropriate libraries for convenience. 
import os

# Ask the user for the csv file name.
NAME = raw_input('What is the csv file name?: ')

# Print the csv file name inputed by the user for debugging purposes.
print 'FOR DEGUBBING, csv file name: %s' % NAME

# Define the paths to the source and target .csv files as arguments for the scp linux command to be executed through the Popen function.
sourcePath = ' dosenet@dosenet.dhcp.lbl.gov:~/config-files/ ' + NAME
targetPath = ' /home/pi/config/config.csv'

# Execute the linux command line to securely copy the file over the Internet. Wait until it executes for this Python script to continue.
p = os.system('scp' + sourcePath + targetPath).wait()

# Print the scp linux command that was executed for debugging purposes.
print 'FOR DEBUGGING, linux command: ', p

'''
Part 2: Updating the dosimeter ID on the network configuration file on the Pi-hat once it has been copied securely over the Internet.
'''

# Ask for the station ID.
ID = input('What is the station ID?: ')

# Open the interfaces file (and call a file handle for it within the program) and update the network ID.
with open('/etc/network/interfaces/interfaces', '+') as netConfig:
  # Search line by line in the interfaces file.
  for line in netConfig:
    # Search for 'wireless-essid' to indicate the place in the code to replace the default Pi-hat ID with the actual station's ID.
    if 'wireless-essid' in line:
      # Create a handle for a new line with the updated station ID to input into the interfaces file.      
      line = 'wireless-essid RPiAdHocNetwork' + ID + '\n'
      netConfig.write(line)


'''
Optional backup section, only works with Python 3.3 and later.

# Open the relevant directory to read/write the network ID on the Pi-hat.
dirConfig = os.open('/etc/network/interfaces')

# Define a function to open files within the directory of interest.
def opendir(path, flags):
  return os.open(path, flags, dir_fd=dirConfig)

# Open the interfaces file (and call a file handle for it within the program) and update the network ID.
with open('interfaces', '+', opener=opendir) as netConfig:
  # Search line by line in the interfaces file.
  for line in netConfig:
    # Search for 'wireless-essid' to indicate the place in the code to replace the default Pi-hat ID with the actual station's ID.
    if 'wireless-essid' in line:
      # Create a handle for a new line with the updated station ID to input into the interfaces file.      
      line = 'wireless-essid RPiAdHocNetwork' + ID + '\n'
      netConfig.write(line)

# Close the file directory.
os.close(dirConfig)
'''
