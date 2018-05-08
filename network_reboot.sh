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

case $1 in
  start)
    logger --stderr -id --tag $LOGTAG "Starting the RaspberryPi as an access point"
    sudo systemctl start hostapd >> $LOG 2>&1
    sudo systemctl start dnsmasq >> $LOG 2>&1
    ;;
  stop)
    echo "Stopping the access point" >> $LOG
    sudo systemctl stop hostapd
    sudo systemctl stop dnsmasq
    ;;
  *)
    echo "Usage: /etc/init.d/network_reboot.sh {start|stop}"
    exit 1
esac

exit 0
