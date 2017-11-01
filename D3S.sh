#! /bin/sh

HOME=/home/pi
DOSENET=$HOME/dosenet-raspberrypi

LOG=/tmp/d3s_manager.log

case "$1" in
  start)
    echo "Starting D3S script" > $LOG
    # -dm runs screen in background. doesn't work without it on Raspbian Jesse.
    sudo python $DOSENET/managers.py --sensor 2 --logfile $LOG >> $LOG 2>&1
    echo "Finished D3S script" >> $LOG
    ;;
  test)
    echo "Starting D3S script in test mode" > $LOG
    sudo python $DOSENET/managers.py --sensor 2 --sender_mode tcp_test --interval 30 --logfile $LOG >> $LOG 2>&1
    ;;
  stop)
    echo "Stopping D3S script" >> $LOG
    sudo pkill -SIGTERM -f managers.py
    ;;
 *)
    echo "Usage: /home/pi/dosenet-raspberrypi/D3S.sh {start|test|stop}"
    exit 1
    ;;
esac

exit 0
