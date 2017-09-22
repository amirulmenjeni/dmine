#
# dmine
#

import sys
import logging

class DmineSpider:
    
    component_group = None
    name = ''
    args = None

    def __init__(self):
        # Check for duplicate name.
        for c in DmineSpider.__subclasses__():
            class_name = self.__class__.__name__
            if (c.name == self.name) and (c.__name__ != class_name):
                logging.error(
                    'There\'s already a crawler with the name \'%s\'. DmineSpider '\
                    'names must be unique. Please change the name of the '\
                    'miner in the class \'%s\' into something else.'
                    % (self.name, self.__class__.__name__)
                )
                sys.exit()
