<<<<<<< HEAD
#
# Author(s): Amirul Menjeni, amirulmenjeni@gmail.com
#
# This is a wrapper for all the spiders.
#
# Usage:
#    dmine.py <domain> <option>



=======
import argparse
import reddit
import logging

def main():
    ##################################################
    # Logger setting.
    ##################################################
    logger_root = logging.getLogger()
    logger_root.setLevel(logging.DEBUG)

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
    parser.add_argument('target', help='Target site to be scrapped e.g. reddit')
    parser.add_argument('-f', '--filter', default='*')
    args = parser.parse_args()

    if args.target == 'reddit':
        reddit_crawler = reddit.RedditCrawler(args)
        reddit_crawler.crawl()
        pass
    elif args.target == 'twitter':
        pass
    elif args.target == 'facebook':
        pass
    else:
        logging.error('Invalid target: %s', args.target) 

if __name__ == '__main__':
   main() 
