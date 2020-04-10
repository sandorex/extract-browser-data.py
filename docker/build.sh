#!/usr/bin/env bash
# THIS SCRIPT IS MEANT TO BE RAN INSIDE THE DOCKER TO INSTALL THE PACKAGES

set -e

# common requirements
function common() {
   echo ':: Installing core utilities'
   apt-get install -qqy --no-install-recommends sudo \
                                                coreutils \
                                                python3 \
                                                python3-pip \
                                                python3-venv

   pip3 --disable-pip-version-check --no-cache-dir install setuptools \
                                                           wheel

   pip3 --disable-pip-version-check --no-cache-dir install tox
}

# firefox only requirements
function firefox() {
   echo ':: Installing Firefox'
   apt-get install -qqy --no-install-recommends firefox \
                                                xvfb \
                                                x11-utils \
                                                wmctrl \
                                                xdotool \
                                                fluxbox
}

# chromium only requirements
function chromium() {
   echo ':: Installing Chromium'

   apt-get install -qqy --no-install-recommends chromium-browser
}

# update repos
apt-get update -qqy

case "${1:-all}" in
   all)
      common
      firefox
      chromium
      ;;
   firefox)
      firefox
      ;;
   chrome|google-chrome|chromium)
      chromium
      ;;
   *)
      common
      ;;
esac

# cleanup
apt autoremove -qqy
apt-get clean
rm -rf /var/lib/apt/lists/* /var/cache/apt/*
