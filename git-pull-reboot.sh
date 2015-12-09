#!/bin/bash
#
# git-pull-reboot.sh
#
# Pull the latest master branch of dosenet-raspberrypi
# Then reboot the computer

DOSENETPATH=/home/pi/dosenet-raspberrypi
cd $DOSENETPATH
logger -s -t dosenet git-pull-reboot.sh is doing a git pull...
# the git pull must be performed by normal user (pi)
sudo -u pi git pull --ff-only

logger -s -t dosenet git-pull-reboot.sh is rebooting now
# the shutdown must be performed by superuser
sudo shutdown -r now
