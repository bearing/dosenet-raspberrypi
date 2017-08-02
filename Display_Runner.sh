#! /bin/sh

HOME=/home/pi
DOSENET=$HOME/dosenet-raspberrypi

for i in $@
do
  case $i in
      stop)
        pyPID=`pgrep -f $Dosenet/OLED_Display.py`
        echo "Stopping OLED Display"
        pkill SIGINT $pyPID
        exit 0
        ;;
  esac
done

echo "Starting OLED Display"
    sudo python $DOSENET/OLED_Display.py $@

exit 0
