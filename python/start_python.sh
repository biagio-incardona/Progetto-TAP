#!/bin/bash
PYTHON_DIR="/usr/src/app/"

cd /usr/src/app/
python ./extract_twitch.py ${CHANNEL_TW} &
python ./extract_youtube.py

