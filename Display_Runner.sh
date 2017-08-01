#! /bin/sh

HOME=/home/pi
DOSENET=$HOME/dosenet-raspberrypi

for i in $@
do
  case $i in
      Stop)
        echo "Stopping Display"
        sudo pkill -SIGTERM -f OLED_Display.py
        exit 0
        ;;
  esac
done

echo "Starting Display"
    sudo python $DOSENET/OLED_Display.py $@
    ;;

exit 0
