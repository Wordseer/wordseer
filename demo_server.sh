#!/bin/bash

source venv/bin/activate 
gunicorn --config=gu_config.py wordseer:app &
