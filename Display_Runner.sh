#! /bin/sh

HOME=/home/pi
DOSENET=$HOME/dosenet-raspberrypi

LOG=/tmp/OLED.log

for i in $@
do
  case $i in
      start)
        echo "Starting OLED Display" >| $LOG
        sudo stdbuf -oL python $DOSENET/OLED_Display.py -Config >> $LOG 2>&1 &
        exit 0
        ;;
      stop)
        sudo pkill -SIGINT -f OLED_Display.py
        echo "Starting OLED Display" >> $LOG &
        exit 0
        ;;
      *)
        echo "Usage: /home/pi/dosenet-raspberrypi/Display_Runner.sh {start|stop}"
        exit 1
        ;;
  esac
done
exit 0
