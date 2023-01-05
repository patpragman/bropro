#!/bin/bash

mkdir venv
python3 -m venv ./venv
source venv/bin/activate
echo "venv set up and activated..."
pip install -r requirements.txt