#!/usr/bin/bash
apt install -y git file make python ffmpeg openssh termux-api python-pip netcat-openbsd

if [ $? -eq 0 ]
then
	pip install -r requirements.txt
fi;
