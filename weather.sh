#! /bin/sh

HOME=/home/pi
DOSENET=$HOME/dosenet-raspberrypi

LOG=/tmp/weather_manager.log

case "$1" in
  start)
    echo "Starting weather sensor script"  > $LOG
    sudo -E python $DOSENET/managers.py --sensor 5 --log --logfile $LOG >>$LOG 2>&1
    echo "Finished weather sensor script"  >> $LOG
    ;;
  test)
    echo "Starting weather sensor script in test mode" > $LOG
    sudo -E python $DOSENET/managers.py --sensor 5 --sender-mode tcp_test --interval 30 --log --logfile $LOG >> $LOG 2>&1
    ;;
  stop)
    echo "Stopping weather sensor script" >> $LOG
    sudo pkill -SIGQUIT -f managers.py
    ;;
 *)
    echo "Usage: /home/pi/dosenet-raspberrypi/weather.sh {start|test|stop}"
    exit 1
    ;;
esac

exit 0
