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

case $1 in
  "10005")
    echo "This is station #10005"
    # commands for station 10005 to run

    # example: system update FOO
    FOOFILE=/home/pi/foo.test
    if [ -f $FOOFILE ]
    then
      echo "System update FOO has already been done. Skipping"
    else
      echo "Performing system update FOO"
      echo "This is system update FOO" >> $FOOFILE
    fi
    sleep 5
    ;;
  *)
    echo "This is everything else"
    # commands for all stations besides 10005 to run
    ;;
esac

# commands for every station to run
