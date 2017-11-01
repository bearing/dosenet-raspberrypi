#! /bin/sh

HOME=/home/pi
DOSENET=$HOME/dosenet-raspberrypi

LOG=/tmp/pocket_manager.log

case "$1" in
  start)
    echo "Starting pocket Geiger script" > $LOG
    # -dm runs screen in background. doesn't work without it on Raspbian Jesse.
    sudo python $DOSENET/managers.py --sensor 1 --logfile $LOG >>$LOG 2>&1
    echo "Finished pocket Geiger script" >> $LOG
    ;;
  test)
    echo "Starting pocket Geiger script in test mode" > $LOG
    sudo python $DOSENET/managers.py --sensor 1 --sender-mode tcp_test --interval 30 --logfile $LOG >> $LOG 2>&1
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
