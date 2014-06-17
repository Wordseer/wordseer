"""
Creates shell using IPython
"""
import sys

from werkzeug import script

from app import models
from app import db

def make_shell():
    try:
        config = sys.argv[1]
    except IndexError:
        config = "dev.cfg"

    return dict(
                models=models,
                db_session=db.session,
                metadata=db.metadata,)

if __name__ == "__main__":

    script.make_shell(make_shell, use_ipython=True)()
