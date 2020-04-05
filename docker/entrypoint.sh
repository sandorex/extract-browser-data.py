#!/usr/bin/env bash
# NOTE THIS SCRIPT IS RAN AS ROOT!!

set -e

DIR="$PWD"/docker

# ensure user owns the directory and all scripts are executable
mkdir -p "$DIR"
chown -R user:user .
chmod -R +x "$DIR"

# shellcheck source=./globals
source "$DIR"/globals

TARGET=${1:-shell}
shift
case "$TARGET" in
   shell|bash|sh)
      # executes bash shell (used for debugging)
      echo ":: Executing the bash shell"
      has_firefox && echo "Firefox $FIREFOX_VERSION_FULL"
      has_chromium && echo "Chrome $CHROME_VERSION"
      exec sudo -E -u user /bin/bash
      ;;
   cache)
      # caches the virtualenv (used in the CI to speed things up)
      # shellcheck source=./python-setup
      source "$DIR"/python-setup
      exit
      ;;
   firefox)
      if ! has_firefox; then
         echo "Firefox not found, cannot run the test"
         exit 1
      fi

      ARG=$1
      shift

      # runs firefox test script
      echo ":: Executing Firefox test script '$ARG'"
      echo "Using Firefox $FIREFOX_VERSION_FULL"
      exec sudo -u user "$DIR"/firefox/"$ARG" "$@"
      ;;
   chrome|google-chrome|chromium)
      if ! has_chromium; then
         echo "Chromium not found, cannot run the test"
         exit 1
      fi

      ARG=$1
      shift

      # runs chromium test script
      echo ":: Executing Chromium test script '$ARG'"
      echo "Using Chromium $CHROMIUM_VERSION"
      exec sudo -u user "$DIR"/chromium/"$ARG" "$@"
      ;;
   *)
      ;;
esac

# run general test script
echo ":: Executing the general test script"
exec sudo -u user "$DIR"/test "$@"
