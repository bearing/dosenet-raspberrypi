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
CONFIGDIR=$HOME/config
LOGTAG=dosenet

CONFIGFILE=$CONFIGDIR/config.csv
PUBLICKEY=$CONFIGDIR/id_rsa_lbl.pub
# if either file is missing, in normal mode, let manager.py raise the IOError

case "$1" in
  start)
    logger --stderr --id --tag $LOGTAG "Waiting for NTP to be synced..."
    ntp-wait -n 10 -s 30
    logger --stderr --id --tag $LOGTAG "Starting DoseNet script"
    # -dm runs screen in background. doesn't work without it on Raspbian Jesse.
    sudo screen -dm python $DOSENET/manager.py
    ;;
  stop)
    logger --stderr --id --tag $LOGTAG "Stopping DoseNet script"
    sudo killall python &
    ;;
  finish)
    sudo kill -s SIGQUIT
    ;;
  test)
    logger --stderr --id --tag $LOGTAG "Testing DoseNet script"
    # allow testing without configfile and/or publickey
    if [ -f $CONFIGFILE ]; then
      if [ -f $PUBLICKEY ]; then
        sudo python $DOSENET/manager.py -c $CONFIGFILE -k $PUBLICKEY --test
      else
        sudo python $DOSENET/manager.py -c $CONFIGFILE --test
      fi
    else
      sudo python $DOSENET/manager.py --test
    fi
    ;;
  *)
    echo "Usage: /etc/init.d/dosenet {start|test|stop}"
    exit 1
    ;;
esac

exit 0
