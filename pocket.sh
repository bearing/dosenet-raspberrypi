#! /bin/sh

HOME=/home/pi
DOSENET=$HOME/dosenet-raspberrypi

LOG=/tmp/pocket_manager.log

case "$1" in
  start)
    echo "Starting pocket Geiger script" > $LOG
    sudo -E python $DOSENET/managers.py --sensor 1 --log --logfile $LOG >>$LOG 2>&1
    echo "Finished pocket Geiger script" >> $LOG
    exit 0
    ;;
  test)
    echo "Starting pocket Geiger script in test mode" > $LOG
    sudo -E python $DOSENET/managers.py --sensor 1 --datalogflag -i 600 --log --logfile $LOG >> $LOG 2>&1
    ;;
  stop)
    echo "Stopping pocket Geiger script" >> $LOG
    sudo pkill -SIGQUIT -f managers.py
    ;;
 *)
    echo "Usage: /home/pi/dosenet-raspberrypi/pocket.sh {start|test|stop}"
    exit 1
    ;;
esac
