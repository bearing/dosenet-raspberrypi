#! /bin/bash
# network-monitor.sh
#
# This is a script to check the wifi network connection and attempt to 
#   reestablish the connection if it has failed
#   but first makes sure there should even be a wifi connection

if ifconfig wlan1 | grep -q "inet addr:198"; then
	echo 'All is well with wlan1'
else
	if /etc/network/interfaces | grep -q "#  wpa-conf /etc/wpa_supplicant/wpa_supplicant.conf" && /etc/network/interfaces | grep -q "#  wireless-essid"; then 
		echo "Not using wlan1"
	else 
		echo 'Internet problem: trying a hard reset of wlan1'
		sudo ifup --force wlan1
	fi
fi
