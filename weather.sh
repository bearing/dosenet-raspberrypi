#! /bin/sh

HOME=/home/pi
DOSENET=$HOME/dosenet-raspberrypi

LOG=/tmp/weather_manager.log

case "$1" in
  start)
    echo "Starting weather sensor script"  > $LOG
    # -dm runs screen in background. doesn't work without it on Raspbian Jesse.
    sudo python $DOSENET/managers.py --sensor 5 --logfile $LOG >>$LOG 2>&1
    echo "Finished weather sensor script"  >> $LOG
    ;;
  test)
    echo "Starting weather sensor script in test mode" > $LOG
    sudo python $DOSENET/managers.py --sensor 5 --test --datalogflag --logfile $LOG >> $LOG 2>&1
    ;;
  stop)
    echo "Stopping weather sensor script" >> $LOG
    sudo pkill -SIGTERM -f managers.py
    ;;
 *)
    echo "Usage: /home/pi/dosenet-raspberrypi/weather.sh {start|test|stop}"
    exit 1
    ;;
esac

exit 0
