#! /bin/sh

HOME=/home/pi
DOSENET=$HOME/dosenet-raspberrypi

LOG=/tmp/d3s_manager.log

case "$1" in
  start)
    echo "Starting D3S script" > $LOG
    sudo -E python2 $DOSENET/managers.py --sensor 2 --log --logfile $LOG >> $LOG 2>&1
    echo "Finished D3S script" >> $LOG
    ;;
  test)
    echo "Starting D3S script in test mode" > $LOG
    sudo -E python2 $DOSENET/managers.py --sensor 2 --test --log --logfile $LOG >> $LOG 2>&1
    ;;
  stop)
    echo "Stopping D3S script" >> $LOG
    sudo pkill -SIGQUIT -f managers.py
    ;;
 *)
    echo "Usage: /home/pi/dosenet-raspberrypi/D3S.sh {start|test|stop}"
    exit 1
    ;;
esac

exit 0
