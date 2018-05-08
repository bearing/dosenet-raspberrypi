#! /bin/sh
#This script runs at startup to boot up the hostapd
#so that the RaspberryPi can act as a reliable standalone network

HOME=/home/pi
LOGTAG=dosenet
LOG=/tmp/network_bootup.log

logger --stderr -id --tag $LOGTAG "Starting the RaspberryPi as an access point"
sudo systemctl start hostapd >> $LOG 2>&1
sudo systemctl start dnsmasq >> $LOG 2>&1

exit 0
