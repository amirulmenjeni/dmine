# main.py
#
# This is module is the starting point of dmine.

import sys
import time
import argparse
import logging
from dmine import Utils, Spider, ComponentGroup, InputGroup, Parser
from spiders import *

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


    parser.add_argument('-w', '--format', default='json',
                        metavar='<file_format>',
                        choices=['json', 'jsonl', 'csv'],
                        dest='file_format',
                        help='The format of the output. The supported '\
                             'file formats are JSON, JSONL, and CSV. '\
                             'By default, output will be written in '\
                             'JSON format.')

    # Mutually exclusive args in relation to the issue
    # of output.
    output_group = parser.add_mutually_exclusive_group()
    output_group.add_argument(
        '-o', '--output', default=None,
        metavar='<output_file>',
        dest='output_file',
        help='The file into which the scraped data is '\
             'written. If not '\
             'specified, then the scraped data will be '\
             'written into STDOUT.'
    )

    output_group.add_argument(
        '-O', '--output-components', default=None,
        metavar='<directory_path>',
        dest='output_dir',
        help='The directory path where the files '\
             'containing the scraped data are saved.  '\
             'The file names are automatically named '\
             'with respect to the name of the component '\
             'the data belongs to.'
    )

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

    # Get list of classes that inherit from Spider class.
    spider_classes = Spider.__subclasses__()

    # Show the scrap filter detail of a given spider and exit.
    if args.filter_detail:
        print_filter_detail(args.filter_detail, spider_classes) 
        sys.exit()

    # Show the input detail of a given spider and exit.
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
                component_group = ComponentGroup(
                                      args.filter, 
                                      spider_name=c.name
                                  )
                instance.setup_filter(component_group)

                # Set up input group.
                input_group = InputGroup(
                                args.spider_input, 
                                spider_name=c.name
                              )
                instance.setup_input(input_group)

                # Parse the component group and input group.
                Parser.parse_scrap_filter(component_group)
                Parser.parse_input_string(input_group)

                # Start spider.
                results = instance.start(component_group, input_group)
                if results is None:
                    logging.warning('No data is generated from %s.start().' %
                                    c.__name__)
                    continue

                # If -O is used, then write the components into its respective
                # files.
                if args.output_dir:
                    Utils.load_components(results,
                                          args.output_dir,
                                          file_format=args.file_format)
                else:
                    # Write the results to a file (or stdout if the option
                    # -o is not given).
                    Utils.to_file(results, args.output_file, 
                                  file_format=args.file_format)

        if not found:
            logging.error('Unable to run spider. '\
                          'No spider named \'%s\' found.' % args.spider)

def report():
    pass

##################################################
# Helper methods
##################################################

# Print the name of every spider created
# (Class that inherits from Spider).
def print_spider_list():
    for c in Spider.__subclasses__():
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
        print('Unable to show scrap filter detail. '\
              'No spider named \'%s\' found.' % spider_name)

def print_input_detail(spider_name, spider_classes):
    found = False
    for c in spider_classes:
        if c.name == spider_name:
            instance = c()
            instance.input_group = InputGroup('') # Don't need input string.
            instance.setup_input(instance.input_group)
            print(instance.input_group.detail())
            found = True
            break
    if not found:
        print('Unable to show spider input detail. '\
              'No spider named \'%s\' found.' % spider_name)

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
    try:
        main() 
    except KeyboardInterrupt:
        print('\nProgram terminated by user.')
        sys.exit(0)
    finally:
        report()

