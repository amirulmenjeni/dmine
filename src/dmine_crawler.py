#
# dmine
#

import sys
import logging

class DmineCrawler:
    
    component_group = None
    name = ''
    args = None

    def __init__(self):
        # Check for duplicate name.
        print(DmineCrawler.__subclasses__())
        for c in DmineCrawler.__subclasses__():
            class_name = self.__class__.__name__
            if (c.name == self.name) and (c.__name__ != class_name):
                logging.error(
                    'There\'s already a crawler with the name \'%s\'. Crawler '\
                    'names must be unique. Please change the name of the '\
                    'crawler in the class \'%s\' into something else.'
                    % (self.name, self.__class__.__name__))
                sys.exit()
