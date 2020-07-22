#!/usr/bin/env bash

if ! [ -x "$(command -v pip3)" ]; then
  echo 'Installing pip3'
  sudo apt-get update && sudo apt-get install -y python3-pip
else
  echo 'Pip3 is installed'
fi
