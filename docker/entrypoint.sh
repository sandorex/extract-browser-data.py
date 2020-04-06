#!/usr/bin/env bash
# NOTE THIS SCRIPT IS RAN AS ROOT!!
# this script just runs the executioner script so there isn't a need for
# building the docker image every damn time

# run shell if needed
[[ "$1" =~ bash|shell|sh ]] && exec sudo -u user /bin/bash

chmod +x "$PWD"/docker/executioner
"$PWD"/docker/executioner "$PWD/docker" "$@"
