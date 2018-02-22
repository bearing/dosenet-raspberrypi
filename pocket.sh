#! /bin/sh

HOME=/home/pi
DOSENET=$HOME/dosenet-raspberrypi

LOG=/tmp/pocket_manager.log

case "$1" in
  start)
    echo "Starting pocket Geiger script" > $LOG
    # -dm runs screen in background. doesn't work without it on Raspbian Jesse.
    sudo -E python $DOSENET/managers.py --sensor 1 --log --logfile $LOG >>$LOG 2>&1
    echo "Finished pocket Geiger script" >> $LOG
    ;;
  test)
    echo "Starting pocket Geiger script in test mode" > $LOG
    sudo -E python $DOSENET/managers.py --sensor 1 --interval 30 --verbosity 3 --log --logfile $LOG >> $LOG 2>&1
    ;;
  stop)
    echo "Stopping pocket Geiger script" >> $LOG
    sudo pkill -SIGTERM -f managers.py
    ;;
 *)
    echo "Usage: /home/pi/dosenet-raspberrypi/pocket.sh {start|test|stop}"
    exit 1
    ;;
esac

exit 0
