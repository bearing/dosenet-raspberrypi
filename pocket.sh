#! /bin/sh

HOME=/home/pi
DOSENET=$HOME/dosenet-raspberrypi

LOG=/tmp/pocket_manager.log

case "$1" in
  start)
    echo "Starting pocket Geiger script" > $LOG
    # -dm runs screen in background. doesn't work without it on Raspbian Jesse.
    sudo python $DOSENET/manager.py --logfile $LOG >>$LOG 2>&1
    echo "Finished pocket Geiger script" >> $LOG
    exit 0
    ;;
  stop)
    echo "Stopping pocket Geiger script" >> $LOG
    sudo pkill -SIGTERM -f manager.py
    exit 0
    ;;
 *)
    echo "Usage: /home/pi/dosenet-raspberrypi/pocket.sh {start|stop}"
    exit 1
    ;;
esac
