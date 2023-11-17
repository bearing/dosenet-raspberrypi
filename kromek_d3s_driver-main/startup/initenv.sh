#!/bin/bash

# This is to make it so sudo is not required to connect via USB to a Kromek D3S device 

# Followed instructions found here:
# https://askubuntu.com/questions/978552/how-do-i-make-libusb-work-as-non-root
# MODE="0666" can be changed to TAG+="uaccess" to limit access to physical users only
# Place .rules file in /etc/udev/rules.d directory
# Unplug and replug in the device

# Might have to add additional idVendor

echo 'SUBSYSTEM=="usb", ATTRS{idVendor}=="2a5a", MODE="0666"' > /etc/udev/rules.d/99-kromek-d3s-usb.rules

echo 'SUBSYSTEM=="tty", ATTRS{idVendor}=="2a5a", MODE="0666"' > /etc/udev/rules.d/99-kromek-d3s-serial.rules

service udev reload
sleep 2
service udev restart