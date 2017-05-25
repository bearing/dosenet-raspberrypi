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

LOG=$HOME/jpyserver.log

case "$1" in
  start)
	# make sure webserver environment is configured properly
	echo "checking that error log can write" > $LOG
	if [ ! -d "/var/log/lighttpd" ]; then
	    sudo mkdir /var/log/lighttpd
	    sudo chown -R www-data /var/log/lighttpd
	fi
    sudo chown www-data:www-data /var/run/lighttpd.pid
    echo "Starting web-server" >> $LOG
    echo "Starting web-server"
    sudo /etc/init.d/lighttpd start
    echo "Updating web code" >> $LOG
    echo "Updating web code"
    cd $HOME/dosenet-web
    sudo -u pi git pull --ff-only
    sudo cp $HOME/dosenet-web/sample_device.html /var/www/html/index.html
    echo "Updating analysis code" >> $LOG
    echo "Updating analysis code"
    cd $HOME/dosenet-analysis
    sudo -u pi git pull --ff-only
    echo "Starting jupyter notebook" >> $LOG
    echo "Starting jupyter notebook"
    sudo -u pi screen -dm jupyter notebook
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
