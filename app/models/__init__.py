import os
import glob

# import all .py files in this directory
# http://stackoverflow.com/a/1057534
modules = glob.glob(os.path.dirname(__file__)+"/*.py")
__all__ = [ os.path.basename(f)[:-3] for f in modules]
