#!/bin/bash

mkdir venv
python3 -m venv ./venv
source venv/bin/activate
echo "venv set up and activated..."
pip install -r requirements.txt

echo "installing requirements"
sudo apt install ffmpeg -y

echo "initiating job for running the server on reboot"
START_STRING="/home/pi/bropro/start.sh >> /home/pi/bropro/bropro.log &"
INITIATOR_FILE="~/.profile"

if grep -q "$START_STRING" "$INITIATOR_FILE"; then
  echo $START_STRING >> $INITIATOR_FILE;
else
  echo "already installed...";
fi
