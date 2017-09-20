#
# dmine
#

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
