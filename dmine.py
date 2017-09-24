#
# Author(s): Amirul Menjeni, amirulmenjeni@gmail.com
#
# This is the main dmine script.
#

import sys
import argparse
import logging
import utils
from spiders import *
from scrap_filter import ComponentGroup
from spider_input import SpiderInput
from dmine_spider import DmineSpider

def main():
    ##################################################
    # Parser.
    ##################################################
    parser = argparse.ArgumentParser(
                description='Dmine is a data scraping tool.',
                epilog='Checkout our github page at http://github.com'\
                        '/amirulmenjeni/dmine.'
             )
    parser.add_argument('-f', '--filter', default='*', 
                        metavar='<scrap_filter_string>',
                        help='Scrap filter string.')

    parser.add_argument('-i', '--input', 
                        metavar='<input_string>',
                        dest='spider_input',
                        help='Spider-specific input string.')

    parser.add_argument('-F', '--filter-detail',
                        metavar='<spider_name>',
                        dest='filter_detail',
                        help='Show scrap filter detail for a spider '\
                             'named <spider_name>.')

    parser.add_argument('-I', '--input-detail',
                        metavar='<spider_name>',
                        dest='input_detail',
                        help='Show input detail for a specific spider '\
                             'named <spider_name>.')

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

    parser.add_argument('-o', '--output', default=None,
                        metavar='<output_file>',
                        dest='output_file',
                        help='The file to store the scraped data.')

    parser.add_argument('-w', '--format', default='json',
                        metavar='<file_format>',
                        choices=['json', 'csv'],
                        dest='file_format',
                        help='The format of the output. The supported '\
                             'file formats are json and csv.')

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

    # Print help if no argument passed.
    if not len(sys.argv) > 1:
        parser.print_help()

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

    # Show the input detail of a given spider.
    if args.input_detail:
        print_input_detail(args.input_detail, spider_classes)
        sys.exit()

    # Run the spider if it is given.
    found = False
    if args.spider:
        for c in spider_classes:
            if c.name == args.spider:
                found = True
                # Create instance.
                instance = c()

                # Set up component group.
                instance.component_group = ComponentGroup(
                                               args.filter, 
                                               spider_name=c.name
                                           )
                instance.setup_filter(instance.component_group)

                # Set up spider input.
                instance.spider_input = SpiderInput(
                                            args.spider_input, 
                                            spider_name=c.name
                                        )
                instance.setup_input(instance.spider_input)

                # Parse the scrap filter and spider input.
                instance.run_parsers()

                # Start spider.
                results = instance.start()
    
                # Write the results to a file (or stdout if the option
                # -o is not given)
                utils.to_file(results, args.output_file, 
                              file_format=args.file_format)

        if not found:
            logging.error('No spider named \'%s\' found.' % args.spider)


##################################################
# Helper methods
##################################################

# Print the name of every spider created
# (Class that inherits from DmineSpider).
def print_spider_list():
    for c in DmineSpider.__subclasses__():
        print(c.name)

# Print the filter detail of a specified spider.
def print_filter_detail(spider_name, spider_classes):
    found = False
    for c in spider_classes:
        if c.name == spider_name:
            instance = c()
            instance.component_group = ComponentGroup('') # Don't need filter
                                                          # string for this.
            instance.setup_filter(instance.component_group)
            print(instance.component_group.detail())
            found = True
            break
    if not found:
        print('No spider named \'%s\' found.' % spider_name)

# Print the input detail of a specified spider.
def print_input_detail(spider_name, spider_classes):
    found = False
    for c in spider_classes:
        if c.name == spider_name:
            instance = c()
            instance.spider_input = SpiderInput('') # Don't need input string.
            instance.setup_input(instance.spider_input)
            print(instance.spider_input.detail())
            found = True
            break
    if not found:
        print('No spider named \'%s\' found.' % spider_name)

# Get the logging enum value of log levels.
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
