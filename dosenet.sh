#! /bin/sh

HOME=/home/pi
DOSENET=$HOME/dosenet-raspberrypi
LOGTAG=dosenet

LOG=/tmp/pocket_manager.log

case "$1" in
  start)
    logger --stderr --id --tag $LOGTAG "Starting DoseNet script"
    echo "Starting pocket Geiger script" > $LOG
    sudo -E python $DOSENET/managers.py --sensor 1 --log --logfile $LOG >>$LOG 2>&1
    echo "Finished pocket Geiger script" >> $LOG
    ;;
  test)
    logger --stderr --id --tag $LOGTAG "Starting DoseNet script in test mode"
    echo "Starting pocket Geiger script in test mode" > $LOG
    sudo -E python $DOSENET/managers.py --sensor 1 --interval 30 --verbosity 3 --log --logfile $LOG >> $LOG 2>&1
    ;;
  stop)
    logger --stderr --id --tag $LOGTAG "Stopping DoseNet script"
    echo "Stopping pocket Geiger script" >> $LOG
    sudo pkill -SIGQUIT -f managers.py
    ;;
 *)
    echo "Usage: /home/pi/dosenet-raspberrypi/pocket.sh {start|test|stop}"
    exit 1
    ;;
esac

exit 0
