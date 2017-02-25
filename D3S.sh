#! /bin/sh
# /etc/init.d/D3S.sh
### BEGIN INIT INFO
# Provides: D3S
# Required-Start: $all
# Required-Stop: $all
# Default-Start: 2 3 4 5
# Default-Stop: 0 1 6
# X-Interactive: false
# Short-Description: DoseNet - sends data for the DoseNet project
### END INIT INFO

HOME=/home/pi
DOSENET=$HOME/dosenet-raspberrypi
LOGTAG=dosenet
CONFIGDIR=$HOME/config
LOGTAG=dosenet

CONFIGFILE=$CONFIGDIR/config.csv
PUBLICKEY=$CONFIGDIR/id_rsa_lbl.pub

case "$1" in
  start)
    logger --stderr --id --tag $LOGTAG "Starting D3S script"
    # -dm runs screen in background. doesn't work without it on Raspbian Jesse.
    sudo screen -dm python $DOSENET/manager_D3S.py
    ;;
  stop)
    logger --stderr --id --tag $LOGTAG "Stopping D3S script"
    sudo pkill -SIGTERM -f manager_D3S.py
    ;;
 *)
    echo "Usage: /etc/init.d/dosenet {start|stop}"
    exit 1
    ;;
esac

exit 0
