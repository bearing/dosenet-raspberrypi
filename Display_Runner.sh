#! /bin/sh

HOME=/home/pi
DOSENET=$HOME/dosenet-raspberrypi

for i in $@
do
  case $i in
      start)
        echo "Starting OLED Display"
        sudo python $DOSENET/OLED_Display.py -Config
        export pyPID=$!
        exit 0
        ;;
      stop)
        echo "Stopping OLED Display"
        kill -s -SIGINT $pyPID
        exit 0
        ;;
      *)
        echo "Usage: /home/pi/dosenet-raspberrypi/Display_Runner.sh {start|stop}"
        exit 1
  esac
done
exit 0
