#! /bin/bash
# system-update.sh
#
# This is a place where we can put system update scripting.
# E.g. modify system files.
# It gets run from git-pull-reboot.sh, AFTER git pull and BEFORE reboot.
#
# One input argument: stationID as a string

# If an update is only to be run once,
#  it should check that it has not been run yet!

# Make sure you check exit codes for whether the update actually worked.
# if [ $? -eq 0]; then echo "successful"; else echo "failed"; fi

LOGTAG=dosenet

case $1 in
  "9999")
    #--------------------------------------------------------------------------
    # BEGIN station update:
    #--------------------------------------------------------------------------
    echo "This is station #9999"
    # commands for this station go here
    ;;
  "32")
    #--------------------------------------------------------------------------
    # BEGIN Etch roof station update: add reboot cron for running d3s monitor
    #--------------------------------------------------------------------------
    echo "This is station #32"
    # fresh checkout - seems to be on a fork of the main repo
    cd /home/pi/dosenet-raspberrypi
    git remote set-url origin https://github.com/bearing/dosenet-raspberrypi.git
    # add d3s data monitor script to crontab
    if sudo crontab -l -u root| grep -q "run-d3s-monitor.sh"; then
      echo 'entry exists'
    else
      echo 'adding entry'
      (sudo crontab -l -u root 2>/dev/null; echo "@reboot /home/pi/dosenet-raspberrypi/run-d3s-monitor.sh") | crontab -
    fi
    ;;
  *)
    echo "This is station #$1"
    # commands for all stations to run
    ;;
esac

#--------------------------------------------------------------------------
# BEGIN system update: git config user.email, user.name to enable git stash
#--------------------------------------------------------------------------
DOSENETPATH=/home/pi/dosenet-raspberrypi
cd $DOSENETPATH

GIT_EMAIL="dosenet.pi@radwatch.berkeley.edu"
GIT_NAME="Anonymous Pi"
CUR_GIT_EMAIL=$(git config --get user.email)
CUR_GIT_NAME=$(git config --get user.name)

if [ ! "$CUR_GIT_EMAIL" = "$GIT_EMAIL" ]; then
  git config user.email "$GIT_EMAIL"
  if [ $? -eq 0 ]; then
    logger --stderr --id --tag $LOGTAG "Successfully updated git user.email"
  else
    logger --stderr --id --tag $LOGTAG "Failed to update git user.email!"
  fi
fi
if [ ! "$CUR_GIT_NAME" = "$GIT_NAME" ]; then
  git config user.name "$GIT_NAME"
  if [ $? -eq 0 ]; then
    logger --stderr --id --tag $LOGTAG "Successfully updated git user.name"
  else
    logger --stderr --id --tag $LOGTAG "Failed to update git user.name!"
  fi
fi
#--------------------------------------------------------------------------
# END system update: git config user.email, user.name to enable git stash
#--------------------------------------------------------------------------
