#!/usr/bin/env python2.7
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
import pdb
# Config
# Location of CoreNLP
CORENLP = "http://nlp.stanford.edu/software/stanford-corenlp-full-2013-06-20.zip"
# Location of pip
PIP = "https://bootstrap.pypa.io/get-pip.py"
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
BOOLEAN_CHOICES = {"y": True, "n": False}

def prompt_user(prompt, choices):
    """Display a prompt to the user.

    Arguments:
        prompt (str): The text to show.
        choices_dict (dict): A list of acceptable choices, case insensitive, as
            the keys, with their values to be returned as the values.

    Returns:
        string: What the user entered, in lowercase.
    """
    insensitive_choices = dict((key.lower(), value) for (key, value) in
        choices.items())

    prompt_string = prompt + " (" + "/".join(choices.keys()) + ") "
    while True:
        result = raw_input(prompt_string).lower()
        if result in insensitive_choices.keys():
            return insensitive_choices[result.lower()]

def download_file(src, dest):
    """Download a file using urllib2.
    """
    source_file = urllib2.urlopen(src)
    with open(dest, "w") as local_file:
        local_file.write(source_file.read())

def install_prerequisites(sudo):
    """Install requirements that we can't install in a virtual environment.

    Arguments:
        sudo (boolean): If ``True``, use sudo.
    """
    system = subprocess.check_output(["uname", "-a"])

    if "Linux" in system and sudo:
        print "Attempting to install prerequisites for linux."
        if "ARCH" in system:
            subprocess.call(["sudo pacman -S libxslt libxml2 jre7-openjdk"],
                shell=True)
        elif "Ubuntu" in system:
            subprocess.call(
                ["sudo apt-get install libxml2 libxslt1.1 openjdk-7-jre"],
                shell=True)

    elif "Darwin" in system:
        print "Mac detected. Compiling requirements for lxml."
        subprocess.call(["STATIC_DEPS=true pip2.7 install lxml"], shell=True)

    else:
        print "Not installing prerequisites."

def install_interactively():
    """Install while prompting the user.
    """
    if not pip_is_installed():
        print ("Pip does not seem to be installed. Pip is required to install "
            "Wordseer. Installing pip requires admin access.")
        get_pip = prompt_user("Install pip?", BOOLEAN_CHOICES)

        install_pip(get_pip)

    print ("The python packages can be installed inside a virtual environment, "
        "which is a cleaner way to install the dependencies. If you do not "
        "have virtualenv installed, you will need admin access to install it.")
    use_virtualenv = prompt_user("Use virtualenv?", BOOLEAN_CHOICES)

    if use_virtualenv:
        make_virtualenv(True)

    print ("You can either perform a full install or a partial install. A "
        "partial install includes just enough to run the interactive wordseer "
        "tool. A full install lets you parse custom collections into the "
        "database.")
    full_install = prompt_user("Perform full install?", BOOLEAN_CHOICES)

    if full_install:
        print "Performing full install."
        install_prerequisites(True)
        setup_stanford_corenlp()
        install_python_packages()
    else:
        print "Performing partial install."
        install_python_packages(REQUIREMENTS_MIN, False)

    sys.exit(0)

def make_virtualenv(sudo_install=False):
    """Install virtualenv if necessary and create a virtual environment.

    Arguments:
        sudo_install (boolean): If True, then it will run sudo to install
            virtualenv via pip if it isn't installed already.
    """
    print "Setting up virtualenv."
    venv_name = "venv"
    packages = subprocess.check_output(["pip2.7", "freeze"])
    if not "virtualenv" in packages:
        if sudo_install:
            print "Installing virtualenv."
            subprocess.call(["sudo", "pip2.7", "install", "virtualenv"])
        else:
            print "Virtualenv not found, not installing."
            return
    else:
        print "Virtualenv already installed."
    subprocess.call(["virtualenv", "--python=python2.7", venv_name])
    venv_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)))
    os.environ["PATH"] = (os.path.join(ROOT_DIRECTORY, venv_name, "bin") + ":" +
        os.environ["PATH"])

def install_python_packages(reqs=REQUIREMENTS_FULL, full=True):
    """Install the required python modules.

    Arguments:
        reqs (str): The requirements file to install from.
        full (boolean): ``True`` if a full installation, ``False`` otherwise.
    """
    print "Installing python dependencies from " + reqs
    system = subprocess.check_output(["uname", "-a"])

    subprocess.call(["pip2.7 install -r " + reqs],
        shell=True)

    if full:
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
    subprocess.call(["python2.7 database.py reset"], shell=True)

def pip_is_installed():
    """Check if the correct version of pip is installed.

    Returns:
        boolean: ``False`` if pip is not installed or installed for the wrong
            version, ``True`` otherwise.
    """
    try:
        pip_version = subprocess.check_output(["pip2.7", "-V"])
    except OSError:
        return False

    return True

def install_pip(sudo):
    """Install pip.

    Arguments:
        sudo (boolean): If ``True``, install pip. Otherwise, the script will
            exit.
    """
    pip_name = "get-pip.py"
    possible_paths = [os.path.join(sys.prefix + "/bin"),
        "/usr/local/bin"]

    # Stop if it's installed
    if pip_is_installed():
        print "Pip is already installed and accessible."
        return

    # If it's not installed, see if we can install it
    if sudo:
        print "Attempting to install pip."
        download_file(PIP, pip_name)
        subprocess.call("sudo python2.7 get-pip.py", shell=True)
    else:
        print "Pip not installed or not accessible, not set to install."

    # If it still doesn't seem installed, look for it
    if not pip_is_installed():
        print "Pip not in PATH, attempting to find."
        for possible_path in possible_paths:
            if "pip" in os.listdir(possible_path):
                print "Found pip in " + possible_path + ", adding to PATH."
                os.environ["PATH"] = possible_path + ":" + os.environ["PATH"]

    if pip_is_installed():
        print "Pip installed successfully."
    else:
        print "Pip install failed. Quitting."
        sys.exit(1)

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

    if args.interactive:
        install_interactively()

    if pip_is_installed():
        install_pip(args.sudo)

    if args.virtualenv:
        make_virtualenv(args.sudo)

    if args.full:
        install_prerequisites(args.sudo)
        install_python_packages(REQUIREMENTS_FULL, True)
        setup_stanford_corenlp()
    else:
        install_python_packages(REQUIREMENTS_MIN, False)

    setup_database()

if __name__ == "__main__":
    main()

