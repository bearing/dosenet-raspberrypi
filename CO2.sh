#! /bin/sh

HOME=/home/pi
DOSENET=$HOME/dosenet-raspberrypi

LOG=/tmp/CO2_manager.log

case "$1" in
  start)
    echo "Starting CO2 sensor script" > $LOG
    # -dm runs screen in background. doesn't work without it on Raspbian Jesse.
    sudo python $DOSENET/managers.py --sensor 4 --log --logfile $LOG >>$LOG 2>&1
    echo "Finished CO2 sensor script" >> $LOG
    ;;
  test)
    echo "Starting CO2 sensor script in test mode" > $LOG
    sudo python $DOSENET/managers.py --sensor 4 --sender-mode tcp_test --interval 30 --log --logfile $LOG >> $LOG 2>&1
    ;;
  stop)
    echo "Stopping CO2 sensor script" >> $LOG
    sudo pkill -SIGTERM -f managers.py
    ;;
 *)
    echo "Usage: /home/pi/dosenet-raspberrypi/CO2.sh {start|test|stop}"
    exit 1
    ;;
esac

exit 0
