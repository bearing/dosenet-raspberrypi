#! /bin/sh
# /etc/init.d/dosenet.sh
### BEGIN INIT INFO
# Provides: dosenet
# Required-Start: $all
# Required-Stop: $all
# Default-Start: 2 3 4 5
# Default-Stop: 0 1 6
# X-Interactive: false
# Short-Description: DoseNet - sends data for the DoseNet project
### END INIT INFO

# setup paths and check config files
HOME=/home/pi
DOSENET=$HOME/dosenet-raspberrypi
LOGTAG=dosenet

LOG=/tmp/manager.log

case "$1" in
  start)
    logger --stderr --id --tag $LOGTAG "Starting all DoseNet scripts"
    echo "Starting all DoseNet scripts" > $LOG
    sudo -u pi -E python $DOSENET/master_manager.py >> $LOG 2>&1
    ;;
  test)
    logger --stderr --id --tag $LOGTAG "Starting all DoseNet scripts in test mode"
    echo "Starting all DoseNet scripts in test mode" > $LOG
    sudo -u pi -E python $DOSENET/master_manager.py --test_mode >> $LOG 2>&1
    ;;
  stop)
    logger --stderr --id --tag $LOGTAG "Stopping all DoseNet scripts"
    echo "Stopping all DoseNet scripts" >> $LOG
    sudo pkill -SIGQUIT python &
    ;;
  *)
    echo "Usage: /etc/init.d/dosenet {start|test|stop}"
    exit 1
    ;;
esac

exit 0
