#! /bin/sh
# /etc/init.d/dosenet.sh
### BEGIN INIT INFO
# Provides: dosenet
# Required-Start: $all
# Required-Stop: $all
# Default-Start: 2 3 4 5
# Default-Stop: 0 1 6
# X-Interactive: false
# Short-Description: DoseNet - sends UDP packets to the GRIM for the DoseNet project
### END INIT INFO
HOME=/home/pi
DOSENET=$HOME/dosenet-raspberrypi
CONFIGDIR=$HOME/config
CONFIGFILE=$CONFIGDIR/config.csv
if [ ! -f $CONFIGFILE ]
then
  # no config file. exit with a user-defined exit code, 64
  echo "Config file $CONFIGFILE not found! Aborting  "
  exit 64
fi

PUBLICKEY=$CONFIGDIR/id_rsa_lbl.pub
if [ ! -f $PUBLICKEY ]
then
  # no publickey. exit with a user-defined exit code, 65
  echo "Public key file  $PUBLICKEY not found! Aborting  "
  exit 65
fi

LOG=/home/pi/sender.log
echo "DoseNet script called @ " > $LOG
date >> $LOG
case "$1" in
  start)
    echo "Starting DoseNet script" >> $LOG
    echo "Starting DoseNet script"
    sudo screen python $DOSENET/udp_sender.py -f $CONFIGFILE --public_key $PUBLICKEY
    date >> $LOG
    ;;
  stop)
    echo "Stopping DoseNet script" >> $LOG
    echo "Stopping DoseNet script"
    date >> $LOG
    sudo killall python &
    ;;
  test)
    echo "Testing DoseNet Script" >> $LOG
    echo "Testing DoseNet Script"
    sudo python $DOSENET/udp_sender.py -f $DOSENET/config-files/$CONFIGFILE --test
    date >> $LOG
    ;;
  *)
    echo "Usage: /etc/init.d/dosenet {start|test|stop}"
    exit 1
    ;;
esac

exit 0
