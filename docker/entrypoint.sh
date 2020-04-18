#!/usr/bin/env bash -l
# this script can run both as user and root

set -e

if command -v firefox &> /dev/null; then
   FIREFOX_PLATFORM_FILE=/usr/lib/firefox/platform.ini

   FIREFOX_BUILDID=$(grep BuildID "$FIREFOX_PLATFORM_FILE")
   FIREFOX_BUILDID=${FIREFOX_BUILDID#*=}
   export FIREFOX_BUILDID

   FIREFOX_VERSION=$(grep Milestone "$FIREFOX_PLATFORM_FILE")
   FIREFOX_VERSION=${FIREFOX_VERSION#*=}
   export FIREFOX_VERSION

   export FIREFOX_VERSION_FULL="${FIREFOX_VERSION}_${FIREFOX_BUILDID}"

   echo "Found Firefox $FIREFOX_VERSION_FULL"
fi

if command -v chromium-browser &> /dev/null; then
   CHROMIUM_VERSION=$(chromium-browser --version)
   CHROMIUM_VERSION=${CHROMIUM_VERSION#* }
   CHROMIUM_VERSION=${CHROMIUM_VERSION%% *}
   export CHROMIUM_VERSION

   export CHROMIUM_VERSION_INTEGER=${CHROMIUM_VERSION//./}

   echo "Found Chromium $CHROMIUM_VERSION"
fi

case "$1" in
   bash|shell|sh)
      exec /bin/bash
      ;;
   *)
      tox "$@"
      ;;
esac
