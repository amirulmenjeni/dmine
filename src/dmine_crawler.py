#
# dmine
#

<<<<<<< HEAD
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
            if (c.name == self.name) and (c.__name__ != class__name):
                logging.error(
                    'There\'s already a crawler with the name \'%s\'. Crawler '\
                    'names must be unique. Please change the name of the '\
                    'crawler in the class \'%s\' into something else.'
                    % (self.name, self.__class__.__name__))
                sys.exit()
=======
from abc import ABCMeta, abstractmethod

class DmineCrawler:
    __metaclass__ = ABCMeta

    component_group = None
    args = None

    # @param args: Parsed argparse argument.
    def __init__(self, component_group, args):
        self.component_group = component_group
        self.args = args

    @abstractmethod 
    def crawl():
        # TO DO: overwrite
        pass
>>>>>>> e086bbbd27c97e5d5fb87423141d76e910dbc790
