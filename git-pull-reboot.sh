#!/bin/bash
#
# git-pull-reboot.sh
#
# May include the branch as an input argument: git-pull-reboot.sh master
#
# Pull the latest from dosenet-raspberrypi
# Then reboot the computer

BRANCH=$1
LOGTAG=dosenet
CONFIGFILE=/home/pi/config/config.csv

DOSENETPATH=/home/pi/dosenet-raspberrypi
cd $DOSENETPATH

# what is my station ID?
if [ -f $CONFIGFILE ]; then
  ID=$(cat $CONFIGFILE | tail -n1 | sed 's/,[a-zA-Z0-9.,-]*//' | sed 's_\r__')
else
  ID=unknown
fi

# git operations:
# `sudo -u pi` is required, because operations must be performed by
#    user `pi`, not root

#--- Clean up the index, working directory, and/or bad history ---
# 1. Get the status
CURRENT_BRANCH=$(git rev-parse --abbrev-ref HEAD)

LABEL_TEXT="Changes not staged for commit:"
ANY_UNSTAGED=$(git status | grep -c "$LABEL_TEXT")

LABEL_TEXT="Changes to be committed:"
ANY_STAGED=$(git status | grep -c "$LABEL_TEXT")

LABEL_TEXT="Your branch is ahead of "
ANY_COMMITS=$(git status | grep -c "$LABEL_TEXT")

LABEL_TEXT=" have diverged,"
ANY_DIVERGENCE=$(git status | grep -c "$LABEL_TEXT")

# 2. start with local commits that didn't get pushed (really shouldn't happen)
if [ $ANY_COMMITS = 1 -o $ANY_DIVERGENCE = 1 ]; then
  TMP=$(date | sed 's/^[A-Z][a-z][a-z]/localchanges/')
  TMP=$(echo $TMP | sed 's/ [0-9][0-9]:[0-9][0-9]:[0-9][0-9] [A-Z]* [0-9]*//')
  NEW_BRANCH_NAME=$(echo $TMP | sed 's/ /-/g')
  # generates a string in the form 'localchanges-May-11'
  LOGMSG="Found local commits! Stashing them in branch $NEW_BRANCH_NAME"
  logger --stderr --id --tag $LOGTAG $LOGMSG
  git branch $NEW_BRANCH_NAME
  EXIT1=$?
  # don't reset to $BRANCH, or else $CURRENT_BRANCH will point to $BRANCH
  #   and be all messed up (divergent)
  git reset --hard origin/$CURRENT_BRANCH
  EXIT2=$?
  if [ $EXIT1 -ne 0 ]; then
    logger --stderr --id --tag $LOGTAG "Failed to create stash branch!"
  fi
  if [ $EXIT2 -ne 0 ]; then
    logger --stderr --id --tag $LOGTAG "Failed to reset branch $BRANCH !"
  fi
fi

# 3. now stash any uncommited local changes in index or working dir
if [ $ANY_UNSTAGED = 1 -o $ANY_STAGED = 1 ]; then
  LOGMSG="Found uncommited local changes! Putting in a git-stash"
  logger --stderr --id --tag $LOGTAG $LOGMSG
  git stash
  if [ $? -ne 0 ]; then
    logger --stderr --id --tag $LOGTAG "Failed to git-stash!"
  fi
fi

# 4. do a fetch on the current branch to ensure we have a copy of
#    the new branch
sudo -u pi git fetch
# it may generate an error if the current branch was deleted on the server.
#   but the new branch still gets fetched.

# now, finally, there should be no reason for checkout and pull to fail.

if [ "$BRANCH" != "" ]
then
  echo "Checkout branch $BRANCH"
  sudo -u pi git checkout $BRANCH
  if [ $? -eq 0 ]; then
    logger --stderr --id --tag $LOGTAG "successfully checked out branch $BRANCH"
  else
    logger --stderr --id --tag $LOGTAG "failed to check out branch $BRANCH !"
  fi
else
  echo "No branch argument, not changing branches"
fi

sudo -u pi git pull --ff-only
if [ $? -eq 0 ]; then
  logger --stderr --id --tag $LOGTAG "git pull successful"
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
sudo shutdown -r now
