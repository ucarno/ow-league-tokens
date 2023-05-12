#!/bin/bash
Xvfb $DISPLAY -screen $DISPLAY 1280x1024x16 & export DISPLAY=:99
python ./src/main.py --nomenu --nowait --docker --profiles default
