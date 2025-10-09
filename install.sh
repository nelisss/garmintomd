#!/bin/bash

if [ -d "venv" ]; then
    echo "Directory venv exists, reinstalling..."
    rm -rf venv
fi

python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt


