# DmineSpider.py
#
# This is an abstract class that all spider must inherit.
#

import sys
import logging
from scrap_filter import Parser
from abc import ABCMeta, abstractmethod

class DmineSpider:
    __metaclass__ = ABCMeta 
    component_group = None
    name = ''
    args = None

    # Initialize the spider class. When a spider object
    # is called to be initialized, its name attribute is
    # checked for duplicate with other spider object.
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

    # This method must be defined by the child classes
    # to define their scrap filter component group.
    @abstractmethod
    def setup_filter(component_group):
        # TODO
        # Overwritten by inheritor. 
        pass
    
    # This shouldn't be overwritten.
    def parse_filter(self):
        Parser.parse_scrap_filter(self.component_group)
