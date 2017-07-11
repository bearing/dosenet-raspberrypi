#! /bin/sh

HOME=/home/pi
DOSENET=$HOME/dosenet-raspberrypi


case "$1" in
  start)
    echo "Starting weather data collection" 
    # -dm runs screen in background. doesn't work without it on Raspbian Jesse.
    sudo python $DOSENET/weather_test.py 
    echo "Finished weather data script"
    ;;
  stop)
    echo "Stopping weather data collection"
    sudo pkill -SIGTERM -f weather_test.py
    ;;
 *)
    echo "Usage: /home/pi/dosenet-raspberrypi/weather.sh {start|stop}"
    exit 1
    ;;
esac

exit 0

