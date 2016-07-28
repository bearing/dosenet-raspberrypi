HOME=/home/pi
DOSENET=$HOME/dosenet-raspberrypi
LOGTAG=dosenet

case "$1" in
  start)
    logger --stderr --id --tag $LOGTAG "Starting D3S script"
    # -dm runs screen in background. doesn't work without it on Raspbian Jesse.
    sudo screen -dm python $DOSENET/manager_D3S.py
    ;;
  stop)
    logger --stderr --id --tag $LOGTAG "Stopping D3S script"
    sudo killall python &
    ;;
 *)
    echo "Usage: /etc/init.d/dosenet {start|test|stop}"
    exit 1
    ;;
esac

exit 0
