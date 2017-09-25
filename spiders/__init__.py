import os
import sys

cwd = os.path.dirname(os.path.realpath(__file__))

# Get a list of spider scripts. 
spider_scripts = []
for f in os.listdir(cwd):
    if os.path.isfile(cwd + '/' + f) and '__init__.py' not in f:
        spider_scripts.append(f[:-3]) # Cut the .py extension.

# This will allow the `spiders` module to import all 
# spider scripts with `from spiders import *`.
__all__ = spider_scripts
