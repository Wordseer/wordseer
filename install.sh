#!/bin/bash

CORENLP=http://nlp.stanford.edu/software/stanford-corenlp-full-2013-06-20.zip
REQUIREMENTS=requirements.txt
CORENLP_DESTINATION="lib/wordseerbackend"
CORENLP_FINAL_NAME="stanford-corenlp"

DIRS=(${CORENLP//\// })
FILENAME=${DIRS[${#DIRS[@]} - 1]}
CORENLP_FINAL_PATH=$CORENLP_DESTINATION"/"$CORENLP_FINAL_NAME

pip install -r $REQUIREMENTS

python database.py create
python database.py migrate

cd $CORENLP_DESTINATION
wget -O $CORENLP_FINAL_NAME".zip" $CORENLP
unzip $CORENLP_FINAL_NAME".zip"
mv ${FILENAME:0:-4} $CORENLP_FINAL_NAME

