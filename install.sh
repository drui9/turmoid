#!/usr/bin/bash
if [ ! -d .venv ]; then
    apt install git axel curl wget file make python3 ffmpeg openssh termux-api python-pip netcat-openbsd

    if [ $? -ne 0 ]; then
        echo 'Install dependencies failed.';
        exit;
    fi
    # --
    python3 -m venv .venv
    if [ $? -ne 0 ]; then
        echo 'Create virtual environment failed. Do it manually.';
        exit;
    else
        .venv/bin/pip install --upgrade pip;
        if [ $? -eq 0 ]; then
            .venv/bin/pip install -r requirements.txt;
        fi;
    fi
else
    .venv/bin/pip install -r requirements.txt;
    if [ $? -ne 0 ]; then
        echo 'Refresh virtual environment failed! (network?)'
    fi;
fi
