#!/bin/env bash

pip install virtualenv
python3 -m virtualenv venv
chmod 744 ./venv/bin/activate
source ./venv/bin/activate
pip install -r requirements.txt
deactivate
