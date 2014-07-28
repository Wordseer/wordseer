#!/bin/bash

# This script installs and sets up an instance of wordseer.

# Config
# Location of stanford-corenlp library
CORENLP="http://nlp.stanford.edu/software/stanford-corenlp-full-2013-06-20.zip"
# Path to requirements file
REQUIREMENTS="requirements.txt"
# Directory to save corenlp to
CORENLP_DESTINATION="lib/wordseerbackend"
# Directory name for the corenlp tree
CORENLP_FINAL_NAME="stanford-corenlp"

DIRS=(${CORENLP//\// })
#FILENAME=${DIRS[${#DIRS[@]} - 1]}
FILENAME=${DIRS[-1]}
CORENLP_FINAL_PATH=$CORENLP_DESTINATION"/"$CORENLP_FINAL_NAME

# Install python requirements
echo "Installing dependencies..."
pip install -r $REQUIREMENTS
python -m nltk.downloader punkt

# Set up the database
echo "Setting up database..."
python database.py create
python database.py migrate

# Download and move stanford-corenlp
echo "Installing stanford-corenlp..."
cd $CORENLP_DESTINATION
curl -o $CORENLP_FINAL_NAME".zip" $CORENLP
unzip $CORENLP_FINAL_NAME".zip"
mv ${FILENAME:0:-4} $CORENLP_FINAL_NAME

# Clean up
echo "Cleaning up..."
rm $CORENLP_FINAL_NAME".zip"

