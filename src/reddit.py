#
# Author(s): Amirul Menjeni (amirulmenjeni@gmail.com
#

import sys
import praw
import logging
import argparse
from dmine_crawler import DmineCrawler
from scrap_filter import ScrapComponent, ScrapOption,\
                         Parser, ValueType, ComponentGroup

class RedditCrawler(DmineCrawler):
    r = None # Reddit prawl instance.
    g = None # This crawler's group of component.
    args = None

    def __init__(self, args):
        DmineCrawler.__init__()
        self.args = args

        ################################################## 
        # Initial PRAW instance.
        ################################################## 
        client_id = 'j8vNY5xeqUemQg' # Acquired from www.reddit.com/prefs/apps
        client_secret = None
        redirect_uri = 'http://localhost:8080'
        user_agent='Mozilla/5.0'

        logging.info('client_id: %s\nclient_secret: %s\nuser_agent: %s' %\
                (client_id, client_secret, user_agent))
    
        self.r = praw.Reddit(
                    client_id=client_id,
                    client_secret=client_secret,
                    redirect_uri=redirect_uri,
                    user_agent=user_agent
                )
        self.r.auth.url(['identity'], redirect_uri, implicit=True)

        ##################################################
        # Initialize scrap components.
        ##################################################
        # Create a component group to hold the components together.
        self.g = ComponentGroup(args.filter)
        self.g.add(ScrapComponent('p', 'post'))
        self.g.add(ScrapComponent('c', 'comment'))
        self.g.add(ScrapComponent('u', 'user'))

        # Add options to the post component.
        p = self.g.get('p')
        p.add_option('t', 'title', ValueType.WORD_FILTER)
        p.add_option('s', 'score', ValueType.INT_RANGE)
        p.add_option('g', 'tag', ValueType.SINGLE_STRING)

        # Add options to the comment component.
        c = self.g.get('c')
        c.add_option('t', 'text', ValueType.WORD_FILTER)
        c.add_option('s', 'score', ValueType.INT_RANGE)
        c.add_option('u', 'user', ValueType.SINGLE_STRING)

        # Add options to the user component.
        u = self.g.get('u')
        u.add_option('b', 'born-date', ValueType.DATE_TIME)
        logging.info(args)
        f = args.filter
        parsed_filter = Parser.parse_scrap_filter(self.g)

        # If the filter is "p{/t:hello^world,~good bye}",
        # this will print ['helo^world', '~good bye']
        # print(parsed_filter['p', 't'])

    def crawl(self):
        pass
