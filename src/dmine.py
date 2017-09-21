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
from reddit import RedditCrawler
from dmine_crawler import DmineCrawler

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

    # Positional argument.
    parser.add_argument('target', help='Target site to be scrapped e.g. reddit')

    # Optional arguments.
    parser.add_argument('-f', '--filter', default='*', 
                        help='Scrap filter string')
    parser.add_argument('-F', '--filter-list', action='store_true',
                        dest='show_filter_list',
                        help='List all defined scrap components and their'
                             'options available for the chosen target.')
    parser.add_argument('-t', '--target-list', action='store_true',
                        dest='show_target_list',
                        help='List all available target.')

    # Parse arguments.
    args = parser.parse_args()

    # Get list of classes that inherit from DmineCrawler.
    crawler_classes = DmineCrawler.__subclasses__()

    # Run the target crawler.
    for c in crawler_classes:
        if c.name == args.target:
            instance = c()
            instance.init(args)
            instance.start()

if __name__ == '__main__':
    main() 
