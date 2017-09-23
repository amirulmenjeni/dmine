# DmineSpider.py
#
# This is an abstract class that all spider must inherit.
#

import sys
import logging
import scrap_filter
import spider_input
from abc import ABCMeta, abstractmethod

class DmineSpider:
    __metaclass__ = ABCMeta 
    component_group = None
    spider_input = None
    name = ''
    args = None

    # Initialize the spider class. When a spider object
    # is called to be initialized, its name attribute is
    # checked for duplicate with other spider object.
    def __init__(self):
        component_group = None
        spider_input = None
        name = ''
        args = None

        # Check for duplicate name.
        for c in DmineSpider.__subclasses__():
            class_name = self.__class__.__name__
            if (c.name == self.name) and (c.__name__ != class_name):
                logging.error(
                    'There\'s already a spider  with the name \'%s\'. '
                    'Spider '\
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
        # Spider dev define his scrap filter here.
        pass

    @abstractmethod
    def setup_input(spider_input):
        # TODO
        # Overwritten by inheritor.
        # Spider dev define his spider input here.
        pass
    
    # This shouldn't be overwritten.
    def run_parsers(self):
        scrap_filter.Parser.parse_scrap_filter(self.component_group)
        spider_input.Parser.parse_input_string(self.spider_input)
