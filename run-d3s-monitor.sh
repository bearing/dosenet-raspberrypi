#!/bin/bash
#
# run-d3s-monitor.sh
#
# Run at startup
#   sleeps for 6 minutes to give the d3s time to aquire the first data point
#   runs the d3s monitor script to check that data is getting through
HOME=/home/pi
DOSENET=$HOME/dosenet-raspberrypi
SLEEPTIME=390

sleep $SLEEPTIME
python $DOSENET/d3s_monitor.py
