#! /bin/sh
# /etc/init.d/dosenet.sh
### BEGIN INIT INFO
# Provides: dosenet
# Required-Start: $all
# Required-Stop: $all
# Default-Start: 2 3 4 5
# Default-Stop: 0 1 6
# X-Interactive: false
# Short-Description: DoseNet - sends data for the DoseNet project
### END INIT INFO

# setup paths and check config files
HOME=/home/pi
CONFIGDIR=$HOME/config

echo "csv file name:"
read NAME

scp dosenet@dosenet.dhcp.lbl.gov:~/config-files/$NAME $CONFIGDIR/config.csv

echo "station ID:"
read ID

awk -v var="RPiAdHocNetwork${ID}" '$1=="wireless-essid" { $0="  "$1" "var } { print; }' /etc/network/interfaces > interfaces
sudo mv interfaces /etc/network/interfaces

echo "configuration updated for station ${ID}!"
exit 0
