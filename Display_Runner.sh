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
        pyPID=$!
        echo $pyPID >| pyPID.txt
        exit 0
        ;;
      stop)
        echo "Stopping OLED Display" >> $LOG
        PIDpy=`cat pyPID.txt`
        sudo kill -s SIGINT $PIDpy
        exit 0
        ;;
      *)
        echo "Usage: /home/pi/dosenet-raspberrypi/Display_Runner.sh {start|stop}"
        exit 1
        ;;
  esac
done
exit 0
