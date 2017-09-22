#
# Author(s): Amirul Menjeni, amirulmenjeni@gmail.com
#
# This is a wrapper for all the spiders.
#
# Usage:
#    dmine.py <domain> <option>

import sys
import argparse
import logging
from spiders import *
from dmine_spider import DmineSpider

def main():
    ##################################################
    # Logger setting.
    ##################################################
    logger_root = logging.getLogger()
    logger_root.setLevel(logging.WARNING)

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
    # Parser.
    ##################################################
    parser = argparse.ArgumentParser(
                description='Dmine is a data scraping tool.'
             )

    parser.add_argument('-f', '--filter', default='*', 
                        help='Scrap filter string')
    parser.add_argument('-s', '--spider', default='',
                        help='The spider to run.')
    parser.add_argument('-l', '--spider-list', action='store_true',
                        help='Show the list of spiders available and exit.',
                        dest='show_spider_list')

    # Parse arguments.
    args = parser.parse_args()

    ##################################################
    # Run according to arguments.
    ##################################################

    # Show a list of spiders available and exit.
    if args.show_spider_list:
        print_spider_list()
        sys.exit()

    # A warning should be given if a scrap filter is given with no
    # spider to use it.
    if args.filter and not args.spider:
        logging.warning(
            'A scrap filter is given but there\'s no spider selected to '\
            'use it. Please specify the spider name with -s or --spider.'
        )

    # Get list of classes that inherit from DmineSpider class.
    crawler_classes = DmineSpider.__subclasses__()

    # Run the spider if it is given.
    if args.spider:
        for c in crawler_classes:
            if c.name == args.spider:
                instance = c()
                instance.init(args)
                instance.start()
        logging.error('No spider named \'%s\' found.' % args.spider)

# Print the name of every spider created
# (Class that inherits from DmineSpider).
def print_spider_list():
    for c in DmineSpider.__subclasses__():
        print(c.name)

# Main function.
if __name__ == '__main__':
    main() 
