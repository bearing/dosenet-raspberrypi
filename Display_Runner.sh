#! /bin/sh

HOME=/home/pi
DOSENET=$HOME/dosenet-raspberrypi

for i in $@
do
  case $i in
      start)
        echo "Starting OLED Display"
        sudo python $DOSENET/OLED_Display.py config
        pyPID=$!
        ;;
      stop)
        echo "Stopping OLED Display"
        kill -s SIGINT $pyPID
        exit 0
        ;;
  esac
done
exit 0
