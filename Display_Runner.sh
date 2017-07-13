#! /bin/sh

HOME=/home/pi
DOSENET=$HOME/dosenet-raspberrypi

case "$1" in
  Start)
    echo "Starting Display"
    sudo python $DOSENET/OLED_Display.py
    ;;
  Stop)
    echo "Stopping Display"
    sudo pkill -SIGTERM -f OLED_Display.py
    ;;
 *)
    echo "Usage: /home/pi/dosenet-raspberrypi/Display_Runner.sh {Start|Stop}"
    exit 1
    ;;
esac

exit 0
