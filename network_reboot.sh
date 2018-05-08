#! /bin/sh
# /etc/init.d/network_reboot.sh
### BEGIN INIT INFO
# Provides: network_reboot
# Required-Start: $all
# Required-Stop: $all
# Default-Start: 2 3 4 5
# Default-Stop: 0 1 6
# X-Interactive: false
# Short-Description: Starts up the Standalone Network
### END INIT INFO
#This script runs at startup to boot up the hostapd
#so that the RaspberryPi can act as a reliable standalone network

HOME=/home/pi
LOGTAG=dosenet
LOG=/tmp/network_bootup.log

sudo systemctl stop hostapd
sudo systemctl stop dnsmasq
logger --stderr -id --tag $LOGTAG "Starting the RaspberryPi as an access point"
sudo systemctl start hostapd >> $LOG 2>&1
sudo systemctl start dnsmasq >> $LOG 2>&1

exit 0
