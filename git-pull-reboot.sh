#!/bin/bash
#
# git-pull-reboot.sh
#
# Pull the latest master branch of dosenet-raspberrypi
# Then reboot the computer

LOGTAG=dosenet
CONFIGFILE=/home/pi/config/config.csv

# if local changes exist, should the script discard by forcing a git checkout or pull?
FORCE_GIT=n

if [ -f $CONFIGFILE ]
then
  ID=$(cat $CONFIGFILE | tail -n1 | sed 's/,[a-zA-Z0-9.,-]*//' | sed 's_\r__')
else
  ID=unknown
fi

DOSENETPATH=/home/pi/dosenet-raspberrypi
cd $DOSENETPATH

# Station-specific stuff
case $ID in
  "7")
    # Foothill College: UDP blocked
    echo "Should switch to a TCP-enabled branch here"
    BRANCH=master
    ;;
  "10005")
    # Test station at Brian's desk right now
    echo "I am sitting on Brian's desk"
    BRANCH=scripting-#24
    ;;
  *)
    echo "I'm something else"
    BRANCH=master
    ;;
esac

# git operations:
# `sudo -u pi` is required, because operations must be performed by
#    user `pi`, not root

sudo -u pi git checkout $BRANCH
if [ $? -eq 0 ]; then
  logger --stderr --id --tag $LOGTAG "successfully checked out branch $BRANCH"
elif [ $FORCE_GIT = "y" ]; then
  sudo -u pi git checkout --force $BRANCH
  if [ $? -eq 0 ]; then
    logger --stderr --id --tag $LOGTAG "successfully (forcefully) checked out branch $BRANCH !"
  else
    logger --stderr --id --tag $LOGTAG "failed to (forcefully) check out branch $BRANCH !"
  fi
else
  logger --stderr --id --tag $LOGTAG "failed to check out branch $BRANCH !"
fi

sudo -u pi git pull --ff-only
if [ $? -eq 0 ]; then
  logger --stderr --id --tag $LOGTAG "git pull successful"
# not sure how to force git here.
else
  logger --stderr --id --tag $LOGTAG "git pull failed !"
fi

sudo $DOSENETPATH/system-update.sh $ID
if [ $? -eq 0 ]; then
  logger --stderr --id --tag $LOGTAG "successfully ran system-update.sh"
else
  logger --stderr --id --tag $LOGTAG "error in system-update.sh !"
fi

logger --stderr --id --tag $LOGTAG "git-pull-reboot.sh is rebooting now"
# the shutdown must be performed by superuser
# sudo shutdown -r now
