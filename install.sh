#!/bin/bash

pip install -r requirements.txt

python database.py create

python database.py migrate

