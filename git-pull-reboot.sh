#!/bin/bash
#
# git-pull-reboot.sh
#
# Pull the latest master branch of dosenet-raspberrypi
# Then reboot the computer

LOGTAG=dosenet
CONFIGFILE=/home/pi/config/config.csv
ID=$(cat $CONFIGFILE | tail -n1 | sed 's/,[a-zA-Z0-9.,-]*//' | sed 's_\r__')

DOSENETPATH=/home/pi/dosenet-raspberrypi
cd $DOSENETPATH

# Station-specific stuff
case $ID in
  "7")
    # Foothill College: UDP blocked
    echo "Should switch to a TCP-enabled branch here"
    BRANCH=master
    ;;
  "8")
    # James Logan High School: on branch logging-testing
    echo "JLHS"
    BRANCH=active-logging
    ;;
  "10005")
    # Test station at Brian's desk right now
    echo "I am sitting on Brian's desk"
    BRANCH=scripting-#24
    ;;
  *)
    echo "I don't know who I am"
    BRANCH=master
    ;;
esac

# git operations:
# `sudo -u pi` is required, because operations must be performed by 
#    user `pi`, not root

logger --stderr --id --tag $LOGTAG "git-pull-reboot.sh is checking out branch $BRANCH ..."
sudo -u pi git checkout $BRANCH

logger --stderr --id --tag $LOGTAG "git-pull-reboot.sh is doing a git pull..."
sudo -u pi git pull --ff-only

logger --stderr --id --tag $LOGTAG "git-pull-reboot.sh is calling system-update.sh..."
sudo $DOSENETPATH/system-update.sh $ID

sleep 10

logger --stderr --id --tag $LOGTAG "git-pull-reboot.sh is rebooting now"
# the shutdown must be performed by superuser
sudo shutdown -r now
