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
if [ ! -f $CONFIGFILE ]
then
  # no config file. exit with a user-defined exit code, 64
  logger -i -t $LOGTAG "Config file $CONFIGFILE not found! Aborting"
  echo "Config file $CONFIGFILE not found! Aborting"
  exit 64
fi

PUBLICKEY=$CONFIGDIR/id_rsa_lbl.pub
if [ ! -f $PUBLICKEY ]
then
  # no publickey. exit with a user-defined exit code, 65
  logger -i -t $LOGTAG "Public key file  $PUBLICKEY not found! Aborting"
  echo "Public key file  $PUBLICKEY not found! Aborting"
  exit 65
fi

case "$1" in
  start)
    logger -i -t $LOGTAG Starting DoseNet script
    echo "Starting DoseNet script"
    # -dm runs screen in background. doesn't work without it on Raspbian Jesse.
    sudo screen -dm python $DOSENET/manager.py -c $CONFIGFILE -k $PUBLICKEY
    ;;
  stop)
    logger -i -t $LOGTAG Stopping DoseNet script
    echo "Stopping DoseNet script"
    sudo killall python &
    ;;
  test)
    logger -i -t $LOGTAG Testing DoseNet script
    echo "Testing DoseNet Script"
    sudo python $DOSENET/manager.py -c $CONFIGFILE -k $PUBLICKEY --test
    ;;
  *)
    echo "Usage: /etc/init.d/dosenet {start|test|stop}"
    exit 1
    ;;
esac

exit 0
