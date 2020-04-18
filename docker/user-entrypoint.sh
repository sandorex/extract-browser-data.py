#!/usr/bin/env bash
# this script is supposed to run the actual test (or shell)

set -e

# first argument is always path to the working directory
cd "$1"
shift

# source the pyenv stuff
# shellcheck disable=SC1091
source /home/user/.profile

case "$1" in
   bash|shell|sh)
      bash
      ;;
   *)
      # run tox
      tox "$@"
      ;;
esac


