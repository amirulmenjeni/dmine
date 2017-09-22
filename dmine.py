#
# Author(s): Amirul Menjeni, amirulmenjeni@gmail.com
#
# This is the main dmine script.
#

import sys
import argparse
import logging
from spiders import *
from scrap_filter import ComponentGroup
from dmine_spider import DmineSpider

def main():
    ##################################################
    # Parser.
    ##################################################
    parser = argparse.ArgumentParser(
                description='Dmine is a data scraping tool.'
             )
    parser.add_argument('-f', '--filter', default='*', 
                        metavar='scrap_filter_string',
                        help='Scrap filter string')

    parser.add_argument('-F', '--filter-detail',
                        metavar='<spider_name>',
                        dest='filter_detail',
                        help='Show scrap filter detail for a specific spider '\
                             'with the name <spider_name>')

    parser.add_argument('-s', '--spider', default='',
                        metavar='<spider_name>',
                        help='Run a spider with the name <spider_name>.')

    parser.add_argument('-l', '--spider-list', action='store_true',
                        dest='show_spider_list',
                        help='Show the list of available spiders and exit.')

    parser.add_argument('-v', '--verbosity', default='WARNING',
                        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 
                                 'CRITICAL'],
                        metavar='<level>',
                        dest='verbosity',
                        help='The verbosity of logging this program. The '\
                             'valid verbosity level is either DEBUG, INFO, '\
                             'WARNING, ERROR or CRITICAL.')

    # Parse arguments.
    args = parser.parse_args()

    ##################################################
    # Logger setting.
    ##################################################
    logger_root = logging.getLogger()
    logger_root.setLevel(get_log_level(args.verbosity))

    # Create console handler.
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    logger_root.addHandler(ch)

    # Create formatter and set the format for console handler.
    formatter = logging.Formatter(
        '[%(asctime)s] %(name)s::%(levelname)s:\n%(message)s'
    )
    ch.setFormatter(formatter)

    # Add the console handler to logger.
    logger_root.addHandler(ch)


    ##################################################
    # Run according to arguments.
    ##################################################

    # Show a list of spiders available and exit.
    if args.show_spider_list:
        print_spider_list()
        sys.exit()

    # Get list of classes that inherit from DmineSpider class.
    spider_classes = DmineSpider.__subclasses__()

    # Show the scrap filter detail of a given spider.
    if args.filter_detail:
        print_filter_detail(args.filter_detail, spider_classes) 
        sys.exit()

    # Run the spider if it is given.
    if args.spider:
        for c in spider_classes:
            if c.name == args.spider:
                # Create instance.
                instance = c()

                # Initialze your spidery needs.
                instance.init()

                # Set up component group.
                instance.component_group = ComponentGroup(
                                               args.filter, 
                                               spider_name=c.name
                                           )
                instance.setup_filter(instance.component_group)

                # Parse the filter.
                instance.parse_filter()

                # Start spider.
                instance.start()
        logging.error('No spider named \'%s\' found.' % args.spider)

# Print the name of every spider created
# (Class that inherits from DmineSpider).
def print_spider_list():
    for c in DmineSpider.__subclasses__():
        print(c.name)

def print_filter_detail(spider_name, spider_classes):
    for c in spider_classes:
        if c.name == spider_name:
            instance = c()
            instance.component_group = ComponentGroup("")
            instance.setup_filter(instance.component_group)
            print(instance.component_group.detail())

def get_log_level(log_level):
    if log_level == 'DEBUG':
        return logging.DEBUG
    if log_level == 'INFO':
        return logging.INFO
    if log_level == 'WARNING':
        return logging.WARNING
    if log_level == 'ERROR':
        return logging.ERROR
    if log_level == 'CRITICAL':
        return logging.CRITICAL

# Main function.
if __name__ == '__main__':
    main() 
