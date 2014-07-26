import pdb
import os
import json
import logging.config

#pdb.set_trace()
logfile = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../logging.json")
logging.config.dictConfig(json.load(open(logfile)))

