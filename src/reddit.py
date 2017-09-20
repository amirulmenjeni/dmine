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
    g = None

    def __init__(self, args):
        DmineCrawler.__init__(self, self.g, args)

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
        p.add_option('t', 'title', ValueType.STRING_COMPARISON)
        p.add_option('s', 'score', ValueType.INT_RANGE)
        p.add_option('l', 'subreddit-list', ValueType.STRING_COMPARISON)
        p.add_option('r', 'subreddit', ValueType.STRING_COMPARISON)
        p.add_option('d', 'time-posted', ValueType.TIME_COMPARISON)

        # Add options to the comment component.
        c = self.g.get('c')
        c.add_option('s', 'score', ValueType.INT_RANGE)

        # Add options to the user component.
        u = self.g.get('u')
        u.add_option('b', 'born-date', ValueType.TIME_COMPARISON)
        logging.info(args)
        f = args.filter
        
        # Finally, parse the scrap filter.
        Parser.parse_scrap_filter(self.g)

    def crawl(self):
        # Example
        p = self.g.get('post')

        # Get each post/submission in r/all. Print 
        for post in self.r.subreddit('all').hot(limit=500):

            # If the filter is "p{/r:x == 'creepy'/s:0 < x <= 1000}",
            # only posts from r/creepy with score from 1 to 1000
            # will be printed out.
            if p.get('subreddit').should_scrap(str(post.subreddit)) and\
               p.get('score').should_scrap(str(post.score)):
                print('--------------------')
                print('TITLE:', post.title)
                print('SUBRE:', post.subreddit)
                print('SCORE:', post.score)


