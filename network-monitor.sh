#! /bin/bash
# network-monitor.sh
#
# This is a script to check the wifi network connection and attempt to 
#   reestablish the connection if it has failed

if ping -q -c 1 www.google.com; then
	echo 'We are live!'
else
	echo 'Internet problem: trying a hard reset of wlan1'
	sudo ifdown wlan1
	sudo ifup wlan1
fi
