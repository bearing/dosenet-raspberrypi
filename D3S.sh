#! /bin/sh

HOME=/home/pi
DOSENET=$HOME/dosenet-raspberrypi

LOG=/tmp/d3s_manager.log

case "$1" in
  start)
    echo "Starting D3S script" > $LOG
    # -dm runs screen in background. doesn't work without it on Raspbian Jesse.
    sudo python $DOSENET/manager_D3S.py --logfile $LOG
    echo "Finished D3S script" >> $LOG
    ;;
  stop)
    echo "Stopping D3S script" >> $LOG
    sudo pkill -SIGTERM -f manager_D3S.py
    ;;
 *)
    echo "Usage: /home/pi/dosenet-raspberrypi/D3S.sh {start|stop}"
    exit 1
    ;;
esac

exit 0
