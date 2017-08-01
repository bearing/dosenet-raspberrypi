#! /bin/sh

HOME=/home/pi
DOSENET=$HOME/dosenet-raspberrypi

for i in $@
do
  case $i in
      stop)
        echo "Stopping OLED Display"
        sudo pkill -SIGTERM -f OLED_Display.py
        exit 0
        ;;
  esac
done

echo "Starting OLED Display"
    sudo python $DOSENET/OLED_Display.py $@

exit 0
