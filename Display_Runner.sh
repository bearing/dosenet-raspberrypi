#! /bin/sh

HOME=/home/pi
DOSENET=$HOME/dosenet-raspberrypi

LOG=/tmp/pocket_manager.log

case "$1" in
  Start)
    echo "Starting Display" > $LOG
    sudo python $DOSENET/OLED_Display.py --logfile $LOG >>$LOG 2>&1
    ;;
  Stop)
    echo "Stopping Display" >> $LOG
    sudo pkill -SIGTERM -f OLED_Display.py
    ;;
 *)
    echo "Usage: /home/pi/dosenet-raspberrypi/Display_Runner.sh {start|stop}"
    exit 1
    ;;
esac

exit 0
