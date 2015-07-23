# WordSeer
## A Text Analysis Environment for Humanities Scholars

[![Stories in Ready](https://badge.waffle.io/wordseer/wordseer.png?label=ready&title=Ready)](https://waffle.io/wordseer/wordseer)
[![Build Status](https://travis-ci.org/Wordseer/wordseer.svg?branch=master)](https://travis-ci.org/Wordseer/wordseer)
[![Documentation](https://readthedocs.org/projects/wordseer/badge/?version=latest)](http://wordseer.readthedocs.org/en/latest/)

[WordSeer](http://wordseer.berkeley.edu/) is a text analysis environment that combines visualization, information retrieval, sensemaking and and natural language processing to make the contents of text navigable, accessible, and useful. You can run WordSeer on your local machine or on a shared server, and you access it via your modern web browser of choice ([Google Chrome](https://www.google.com/chrome/browser/desktop/index.html) works best, though).

If you're a scholar who's interested in using Wordseer for your research, read on. If you want to learn more about how to contribute to WordSeer's ongoing design and development, take a look at our [Guidelines for Contributors](https://github.com/Wordseer/wordseer/blob/master/CONTRIBUTING.markdown).

You can find much more information on WordSeer, including demo videos, use case studies, and background research, at [wordseer.berkeley.edu](http://wordseer.berkeley.edu).

## Installation

Be prepared: you may have to do a little command-line voodoo to install and launch WordSeer! But once it is up and running, you will access it through a web browser.

### Prerequisites

Before attempting to install WordSeer, make sure your computer has the following software installed:

- [Python 2.7](https://python.org/download) (Python 3.x is NOT supported at this time)
- [Java 1.8 or later](https://www.java.com/en/download/manual.jsp)

### Download

The latest release of WordSeer is available as a .zip file from this GitHub repository 
[here](https://github.com/Wordseer/wordseer/archive/master.zip). Download this file and 
extract its contents wherever you want; WordSeer will keep all the files it needs to run 
in this folder.

### For Mac OS X users

tktk

### For Windows users

Double click on `install.bat` in the folder where you extracted WordSeer and follow the prompts.
You may need administrator privileges to complete some parts of the installation.

### For Linux users

Open the extracted WordSeer folder in your command-line terminal.

From this directory, start the install process by entering the following command:

    ./install.py -i

This will launch the interactive installer which will guide you through the
simple installation process with a series of questions. You may need administrator privileges
to complete some parts of the installation.

If you know what you want, run `install.py -h` to view known console flags.

## Starting Wordseer

After installation has completed, you are ready to run WordSeer.

### Linux/OS X

Run `wordseer.py`:

    ./wordseer.py
    
You will see a console window with an IP address. Navigate
to that address in your browser and you should see the WordSeer welcome
screen.

### Windows

Double click on `wordseer.bat`.

You will see a console window with an IP address. Navigate
to that address in your browser and you should see the WordSeer welcome
screen.

## Using WordSeer for the first time

You will be asked to register and log in to use WordSeer; this allows multiple users
to collaborate on analysis projects, and the account information you enter will only
be stored locally on your computer. There is no mothership for WordSeer to talk to, and 
we don't collect any information from you. 

Once you've logged in, you can create new Projects, which are self-contained collections
of documents that you want to analyze. To explore your documents in WordSeer, you must 
first upload and process them. WordSeer only accepts documents in **XML format** at this point.

### Analyzing documents with WordSeer

If you want to test out WordSeer before loading your own collection, we have included several
example collections with this download; they are located in the `tests/data/` directory. Each 
folder in this directory contains a number of `.xml` files and one `.json` file. To 
explore a demo collection, create a new Project, upload the XML files from your chosen directory
in the "Documents" tab, and upload the JSON file under the "Structure Maps" tab. Then click the 
"Process Documents" button (you may need to reload the page after uploading to activate this button)
and choose a structure map from the list that appears (there should be only one, and it should be 
the one you just uploaded).

Take note: **processing can be SLOW.** The good news, though, is that you only need to do it once. 
Depending on the number, length, and complexity of the documents in your project, it may take anywhere 
from 30 seconds to several hours. Processing runs in the background and you can close the browser window
and continue using your computer normally while it is in progress, but it will be paused and may encounter 
errors if your computer goes to sleep. If you close the terminal window where WordSeer was launched from, or 
shut off your computer, the process will be interrupted and you will have to start over with a 
new project. The "Processing Logs" tab on the project page will keep you updated on
WordSeer's progress; when processing is complete, the "Explore data" button will become active; 
clicking it launches the WordSeer text analysis environment for that project.

You can learn more about the analysis capabilities of WordSeer and view some video demos and tutorials 
at our [website](http://wordseer.berkeley.edu/).

### Importing your own document collection into WordSeer

If you've gotten this far, you probably have your own collection of documents that you want to analyze.
Good news: as of version 4.0, WordSeer includes a Structure Mapper tool that lets you tell
WordSeer what information you want to extract from the XML documents you upload. To access it, upload 
your documents to a new Project and click the "Map document structure" button. The interface includes
detailed instructions for using it; in addition, here are a few things to keep in mind:

- You can make as many Structure Maps as you want, but in the end you will have to choose just one to process the entire collection with; this means all the documents in your Project must follow the same schema.
- WordSeer's Structure Mapper uses just one of your documents at a time as a model for the entire collection; make sure you choose one that is as complete as possible in representing the schema of your documents.  

The Structure Mapper creates a JSON file just like the ones that come bundled with our example projects.
Once you have created one, you can process and analyze the project in the same manner as 
described above. 

## Help and feedback

WordSeer is open-source beta software, so you are likely to encounter bugs as you use it.
Feel free to report them on our [GitHub Issues page](https://github.com/Wordseer/wordseer/issues) 
(but please check to see if someone else already has, so you don't create a duplicate report). 

We'd also love to hear from you with any feedback, good or bad! We want to know who's 
out there using WordSeer so we can understand how the community is using it and hopefully
continue developing and improving it. The WordSeer project is directed by [Prof. Marti Hearst](http://people.ischool.berkeley.edu/~hearst/) 
at the University of California, Berkeley, School of Information; you may contact her via email 
at hearst@berkeley.edu.

## License information 

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
