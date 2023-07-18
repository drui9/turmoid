#!/usr/bin/bash
if [ ! -d .venv ]; then
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
        exit;
    fi;
fi

