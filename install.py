#!/usr/bin/env python
"""Installtion script for WordSeer.
"""
import argparse
import shutil
import os
import sys
import subprocess
import urllib2
import zipfile
import gzip
import glob

# Config
# Location of CoreNLP
CORENLP = "http://nlp.stanford.edu/software/stanford-corenlp-full-2013-06-20.zip"
# Location of libxml for macs
LIBXML_MAC = "http://www.explain.com.au/download/combo-2007-10-07.dmg.gz"
# Path to requirements file
REQUIREMENTS_FULL = "requirements.txt"
REQUIREMENTS_MIN = "requirements_min.txt"
# Directory to save corenlp to
CORENLP_LOCAL_DIR = "./"
# Directory name for the corenlp tree
CORENLP_LOCAL_NAME = "stanford-corenlp"

CORENLP_LOCAL_PATH = os.path.join(CORENLP_LOCAL_DIR, CORENLP_LOCAL_NAME)
CORENLP_ZIP_DIRECTORY = os.path.splitext(os.path.basename(CORENLP))[0]
ROOT_DIRECTORY = os.path.abspath(os.path.dirname(__file__))

def prompt_user(prompt, choices):
    """Display a prompt to the user.

    Arguments:
        prompt (str): The text to show.
        choices (list): A list of acceptable choices, case insensitive.

    Returns:
        string: What the user entered, in lowercase.
    """
    choices = [choice.lower() for choice in choices]
    prompt_string = prompt + " (" + "/".join(choices) + ") "
    while True:
        result = raw_input(prompt_string).lower()
        if result in choices:
            return result

def download_file(src, dest):
    """Download a file using urllib2.
    """
    source_file = urllib2.urlopen(src)
    with open(dest, "w") as local_file:
        local_file.write(source_file.read())

def install_prerequisites():
    """Install requirements that we can't install in a virtual environment.
    """
    system = subprocess.check_output(["uname", "-a"])

    if "Linux" in system:
        print "Attempting to install prerequisites for linux."
        if "ARCH" in system:
            subprocess.call(["sudo pacman -S libxslt libxml2 jre7-openjdk"],
                shell=True)
        elif "Ubuntu" in system:
            subprocess.call(
                ["sudo apt-get install libxml2 libxslt1.1 openjdk-7-jre"],
                shell=True)

    elif "Darwin" in system:
        print "Mac detected, no prerequisites to install yet."
#        print "Installing prerequisites for mac."
        
#        download_file(LIBXML_MAC, "libxml.dmg.gz")

#        with gzip.GzipFile("libxml.dmg.gz") as local_zip,\
#            open("libxml.dmg", "w") as local_dmg:
#                local_dmg.write(local_zip.read())
#        os.remove("libxml.dmg.gz")
#        mounting = subprocess.check_output(["hdiutil", "mount", "libxml.dmg"])
#        mountpoint = mounting.split("\n")[-2].split()[2]
#
#        frameworks = glob.glob(mountpoint + "/*.framework")
#        for framework in frameworks:
#            subprocess.call(["sudo", "cp", "-r", framework,
#                "/Library/Frameworks"])
#
#        executables = [os.path.join(mountpoint, "xmllint"),
#                os.path.join(mountpoint, "xsltproc"),
#                os.path.join(mountpoint, "xmlcatalog")]
#        for executable in executables:
#            subprocess.call(["sudo", "cp", executable, "/usr/bin"])
#        subprocess.call(["hdiutil", "unmount", mountpoint])
#
    else:
        print ("Could not identify operating system, prerequisite installation "
        "failed.")

def install_interactively():
    """Install while prompting the user.
    """
    print ("You can either perform a full install or a partial install. A "
        "partial install includes just enough to run the interactive wordseer "
        "tool. A full install lets you parse custom collections into the "
        "database.")
    full_install = prompt_user("Perform full install?", ["y", "n"])

    if full_install == "y":
        print "Performing full install."
        #install_prerequisites()
        setup_stanford_corenlp()

    else:
        print "Performing partial install."

    print ("The python packages can be installed inside a virtual environment, "
        "which is a cleaner way to install the dependencies. If you do not "
        "have virtualenv installed, you will need admin access to install it.")
    use_virtualenv = prompt_user("Use virtualenv?", ["y", "n"])

    if use_virtualenv == "y":
        make_virtualenv(True)

    if full_install == "y":
        install_python_packages()
    else:
        install_python_packages(REQUIREMENTS_MIN)

    sys.exit(0)

def make_virtualenv(sudo_install=False):
    """Install virtualenv if necessary and create a virtual environment.

    Arguments:
        sudo_install (boolean): If True, then it will run sudo to install
            virtualenv via pip if it isn't installed already.
    """
    print "Setting up virtualenv."
    venv_name = "venv"
    packages = subprocess.check_output(["pip", "freeze"])
    if not "virtualenv" in packages:
        if sudo_install:
            print "Installing virtualenv."
            subprocess.call(["sudo", "pip", "install", "virtualenv"])
        else:
            print "Virtualenv not found, not installing."
            return
    else:
        print "Virtualenv already installed."
    subprocess.call(["virtualenv", "--python=python2.7", venv_name])
    #subprocess.call(["source venv/bin/activate"], shell=True)
    venv_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)))
    os.environ["PATH"] = (os.path.join(ROOT_DIRECTORY, venv_name, "bin") + ":" +
        os.environ["PATH"])

def install_python_packages(reqs=REQUIREMENTS_FULL):
    """Install the required python modules.

    Arguments:
        reqs (str): The requirements file to install from.
    """
    print "Installing python dependencies from " + reqs

    if reqs == REQUIREMENTS_FULL:
        print "Compiling requirements for lxml."
        subprocess.call(["STATIC_DEPS=true pip install lxml"], shell=True)
    
    subprocess.call(["pip install -r " + REQUIREMENTS_FULL],
        shell=True)

    subprocess.call(["python -m nltk.downloader punkt"], shell=True)

def setup_stanford_corenlp(force=False):
    """Download and move Stanford CoreNLP to the expected place.

    Arguments:
        force (boolean): If ``False``, then don't download if
            ``CORENLP_LOCAL_PATH`` exists. Otherwise, download anyway.
    """
    temp_corenlp_name = "corenlp.zip"

    if not force:
        if not os.path.isdir(CORENLP_LOCAL_PATH):
            force = True

    if force:
        print "Installing CoreNLP"
        source_file = urllib2.urlopen(CORENLP)

        with open(temp_corenlp_name, "w") as local_file:
            print "Downloading..."
            local_file.write(source_file.read())

        with zipfile.ZipFile(temp_corenlp_name, "r") as local_zip:
            print "Extracting..."
            local_zip.extractall()

        shutil.move(CORENLP_ZIP_DIRECTORY, CORENLP_LOCAL_PATH)
        print "Cleaning up..."
        os.remove("corenlp.zip")
        print "Done"

    else:
        print "CoreNLP seems to be installed, skipping"

def setup_database():
    """Set up the database.
    """
    print "Setting up database..."
    subprocess.call(["python database.py reset"], shell=True)

def main():
    """Perform the installation process.
    """
    parser = argparse.ArgumentParser(
        description="Install wordseer's requirements.")
    parser.add_argument("-i", "--interactive", action="store_true",
        help="Run interactively. This supersedes all other options.")
    parser.add_argument("-v", "--virtualenv", action="store_true",
        help="Install python requirements into a virtual environment.")
    parser.add_argument("--sudo", action="store_true",
        help="Use sudo to install some dependencies, if necessary")

    install_type = parser.add_mutually_exclusive_group()
    install_type.add_argument("-f", "--full", action="store_true",
        help="Install everything.", default=True)
    install_type.add_argument("-p", "--partial", action="store_true",
        help="Install only enough to run the wordseer tool.", default=False)

    args = parser.parse_args()

    if args.virtualenv:
        make_virtualenv(args.sudo)

    if args.interactive:
        install_interactively()

    if args.sudo and args.full:
        install_prerequisites()

    if args.full:
        install_python_packages(REQUIREMENTS_FULL)
        setup_stanford_corenlp()
    else:
        install_python_packages(REQUIREMENTS_MIN)

if __name__ == "__main__":
    main()

