#! /bin/sh
# /etc/init.d/jpyserver.sh
### BEGIN INIT INFO
# Provides: jpyserver
# Required-Start: $all
# Required-Stop: $all
# Default-Start: 2 3 4 5
# Default-Stop: 0 1 6
# X-Interactive: false
# Short-Description: jpyserver - starts a jupyter notebook for students to play with locally
### END INIT INFO

HOME=/home/pi
DOSENET=$HOME/dosenet-raspberrypi

# make sure webserver environment is configured properly
echo "checking that error log can write"
if [ ! -d "/var/log/lighttpd" ]; then
    sudo mkdir /var/log/lighttpd
    sudo chown -R www-data /var/log/lighttpd
fi

LOG=$HOME/jpyserver.log
JLOG=$HOME/jupyter.log

case "$1" in
  start)
    echo "Starting web-server" >> $LOG
    echo "Starting web-server"
    sudo /etc/init.d/lighttpd start
    echo "Starting jupyter notebook" >> $LOG
    echo "Starting jupyter notebook"
    jupyter notebook >& $JLOG &
    date >> $LOG
    ;;
  stop)
    echo "Stopping jupyter-notebook" >> $LOG
    echo "Stopping jupyter-notebook"
    date >> $LOG
    sudo killall jupyter-notebook
    ;;
  test)
    echo "Testing web-server script" >> $LOG
    echo "Testing web-server script"
    date >> $LOG
    ;;
  *)
    echo "Usage: /etc/init.d/jpyserver.sh {start|test|stop}"
    exit 1
    ;;
esac

exit 0
