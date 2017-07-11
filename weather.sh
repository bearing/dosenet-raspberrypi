#! /bin/sh

HOME=/home/pi
DOSENET=$HOME/dosenet-raspberrypi

LOG=/tmp/weather_manager.log

case "$1" in
  start)
    echo "Starting weather data collection"  > $LOG
    # -dm runs screen in background. doesn't work without it on Raspbian Jesse.
    sudo python $DOSENET/weather_test.py  >> $LOG
    echo "Finished weather data script"  >> $LOG
    ;;
  stop)
    echo "Stopping weather data collection"  >> $LOG
    sudo pkill -SIGTERM -f weather_test.py   >> $LOG
    ;;
 *)
    echo "Usage: /home/pi/dosenet-raspberrypi/weather.sh {start|stop}"
    exit 1
    ;;
esac

exit 0

