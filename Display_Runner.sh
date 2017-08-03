#! /bin/sh

HOME=/home/pi
DOSENET=$HOME/dosenet-raspberrypi

LOG=/tmp/OLED.log

for i in $@
do
  case $i in
      start)
        echo "Starting OLED Display" >| $LOG
        sudo python $DOSENET/OLED_Display.py -Config >> $LOG &
        exit 0
        ;;
      stop)
        echo "Stopping OLED Display" >> $LOG
        sudo pkill -SIGINT -f OLED_Display.py
        exit 0
        ;;
      *)
        echo "Usage: /home/pi/dosenet-raspberrypi/Display_Runner.sh {start|stop}"
        exit 1
        ;;
  esac
done
exit 0
