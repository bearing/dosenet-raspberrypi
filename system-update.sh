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

case $1 in
  "8")
    echo "This is station #8"
    # commands for station 1 to run
    ;;
  *)
    echo "This is everything else"
    # commands for all stations besides 1 to run
    ;;
esac

# commands for every station to run

