"""Installtion script for WordSeer.
"""
import argparse
import shutil
import os
import pdb
import subprocess
import urllib2
import zipfile

# Config
# Location of CoreNLP
CORENLP = "http://nlp.stanford.edu/software/stanford-corenlp-full-2013-06-20.zip"
# Path to requirements file
REQUIREMENTS = "requirements.txt"
# Directory to save corenlp to
CORENLP_LOCAL_DIR = "./"
# Directory name for the corenlp tree
CORENLP_LOCAL_NAME = "stanford-corenlp"

CORENLP_LOCAL_PATH = os.path.join(CORENLP_LOCAL_DIR, CORENLP_LOCAL_NAME)
CORENLP_ZIP_DIRECTORY = os.path.splitext(os.path.basename(CORENLP))[0]

def main():
    """Perform the installation process.
    """
    parser = argparse.ArgumentParser(
        description="Install wordseer's requirements.")
    root_method = parser.add_mutually_exclusive_group()
    root_method.add_argument("--sudo", action="store_true",
        help="Use sudo to install some dependencies")
    root_method.add_argument("--su", action="store_true",
        help="Use su to become root to install some dependencies")
    args = parser.parse_args()

    if args.sudo:
        # Install things with sudo
        pass

    elif args.su:
        # Install things with su
        pass

    # Install things
    print "Installing python dependencies"
    subprocess.call(["pip install -r " + REQUIREMENTS],
        shell=True)

    subprocess.call(["python -m nltk.downloader punkt"], shell=True)

    print "Setting up database..."
    subprocess.call(["python database.py reset"], shell=True)

    print "Installing stanford-corenlp"
    source_file = urllib2.urlopen(CORENLP)
    with open("corenlp.zip", "w") as local_file:
        local_file.write(source_file.read())

    with zipfile.ZipFile("corenlp.zip", "r") as local_zip:
        local_zip.extractall()

    shutil.move(CORENLP_ZIP_DIRECTORY, CORENLP_LOCAL_PATH)

    print "Cleaning up..."
    os.remove("corenlp.zip")


if __name__ == "__main__":
    main()

