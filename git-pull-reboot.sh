#!/bin/bash
#
# git-pull-reboot.sh
#
# Pull the latest master branch of dosenet-raspberrypi
# Then reboot the computer

DOSENETPATH=$HOME/gh/dosenet-raspberrypi
cd $DOSENETPATH
echo "Doing a git pull..."
git pull origin master

echo " "
echo "Rebooting in 5..."
sudo shutdown -r 5
