# main.py
#
# This is module is the starting point of dmine.

import sys
import time
import argparse
import threading
import time
import logging
import math
from dmine import Utils, Spider, ScrapeFilter, ComponentLoader
from spiders import *

def main():
    ##################################################
    # Parser.
    ##################################################
    parser = argparse.ArgumentParser(
                description='Dmine is a data scraping tool.',
                epilog='Check out our github page at http://github.com'\
                       '/amirulmenjeni/dmine.'
             )
    parser.add_argument('-f', '--filter', default='', 
                        metavar='<scrap_filter_string>',
                        help='Scrape Filter Language string.')

    parser.add_argument('-i', '--input', 
                        metavar='<input_string>',
                        dest='spider_input',
                        help='Spider input string.')

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

    parser.add_argument('-t', '--timeout', default=math.inf,
                        type=arg_timeout,
                        metavar='<duration>',
                        dest='timeout',
                        help='The time taken before a spider will be '\
                             'pre-empted to halt. By default, spider '\
                             'will run indefinitely, or when it is '\
                             'interrupted by the user. The time format '\
                             'must be either S, M:S, H:M:S, or D:H:M:S, '\
                             'where D, H, M and S are positive integers and '
                             'represents days, hours, minutes and seconds '\
                             'respectively.')
    
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
             'containing the scraped data for each components are saved.  '\
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
                spider_thread = threading.Thread(
                            target=run_spider,
                            args=(c(), args),
                        )
                spider_thread.start()
                
        if not found:
            logging.error('Unable to run spider. '\
                          'No spider named \'%s\' found.' % args.spider)


# @param instance: An instance of a Spider class.
# @param args: Parsed argparse object.
#
# Spider running on its thread.
def run_spider(instance, args):
    timeout = time.time() + args.timeout

    # Set up scrape filter.
    scrape_filter = ScrapeFilter(
                          args.filter, 
                          spider_name=instance.name
                      )
    instance.setup_filter(scrape_filter)
    scrape_filter.run_interpreter()

    # Start spider.
    results = instance.start(scrape_filter)

    if results is None:
        logging.warning('No data is generated from %s.start().' %
                        type(instance).__name__)
        return

    # Iterate of over the results generator.
    # If a timer is used, then stop the iteration when
    # timeout.
    #
    # If the item in the iteration is a ComponentLoader,
    # then obtain the ComponentLoader's data (this is because
    # some spiders yield ComponentLoader object instead of dict object).
    #
    # The iteration stops when there's nothing more to iterate or when
    # a timeout forces it to stop.
    for r in results:
        if time.time() > timeout:
            break

        if isinstance(r, ComponentLoader):
            data = r.data

        if args.output_dir:
            Utils.component_loader_to_file(
                r, args.output_dir, file_format=args.file_format
            )
        else:
            Utils.dict_to_file(data, args.output_file, 
                          file_format=args.file_format)

##################################################
# Args parsing methods
##################################################

# @param string: The string obtained from argparse.
#
# The string is expected to be integer of pattern
# s, m:s, h:m:s, or d:h:m:s where s, m, h, d are integers,
# representing seconds, minutes, hours and days respectively.
def arg_timeout(string):
    times = string.split(':')

    if len(times) > 4:
        msg = 'The time format should be in S, M:S, H:M:S, or '\
              'D:H:M:S only, '\
              'where S, M, H, and D represents seconds, minutes, hours, '\
              'and days respectively.'
        raise argparse.ArgumentTypeError(msg)


    # Check if each time component (s, m, h, d) is digit.
    for t in times:
        if not t.isdigit():
            msg = '\'%s\' in \'%s\' is not a digit.' % (t, string)
            raise argparse.ArgumentTypeError(msg)

    # Check if each time component's value is within its
    # expected range.
    c = 0
    for t in reversed(times):
        valid = {
            0: lambda x: 0 <= x < 60,    # seconds
            1: lambda x: 0 <= x < 60,    # minutes
            2: lambda x: 0 <= x < 24,    # hours
            3: lambda x: 0 <= x          # days
        }
        if not valid[c](int(t)):
            msg = 'Invalid time format: \'%s\'' % string 
            raise argparse.ArgumentTypeError(msg)
        c += 1

    time_list = []
    for t in reversed(times):
        time_list.append(int(t))
    
    convert = {
        0: 1,             
        1: 60,         # A minute to seconds
        2: 3600,       # An hour to seconds
        3: 86400       # A day to seconds
    }
    
    # Return the time in seconds.
    return sum([time_list[i] * convert[i] for i in range(len(time_list))])

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
            instance.scrape_filter = ScrapeFilter('') # Don't need filter
                                                          # string for this.
            instance.setup_filter(instance.scrape_filter)
            print(instance.scrape_filter.detail())
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

