import os
import re
import sys

dir_path = os.path.dirname(os.path.realpath(__file__))

# Get a list of spider scripts. 
spider_scripts = []
for f in os.listdir(dir_path):
    if os.path.isfile(dir_path + '/' + f) and re.match('[^_.]\w+\.py', f):
        spider_scripts.append(f[:-3]) # Cut the .py extension.

# This will allow the `spiders` module to import all 
# spider scripts with `from spiders import *`.
__all__ = spider_scripts
