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
    sudo pkill --TERM -f manager_D3S.py
    ;;
 *)
    echo "Usage: /etc/init.d/dosenet {start|stop}"
    exit 1
    ;;
esac

exit 0
