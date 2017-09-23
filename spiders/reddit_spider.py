#
# Author(s): Amirul Menjeni (amirulmenjeni@gmail.com
#

import sys
import praw
import logging
from itertools import chain
from dmine_spider import DmineSpider
from scrap_filter import ScrapComponent, ValueType
from spider_input import Input, SpiderInput, InputType, Parser

class RedditSpider(DmineSpider):
    r = None # Reddit prawl instance.
    name = 'reddit'

    def setup_filter(self, component_group):
        # Add scrap components.
        component_group.add(
            ScrapComponent(
                'post',
                symbol='p', 
                info='A user submitted content to a subreddit '\
                     '(i.e. submission). Not to be confused with a comment.'
            )
        )
        component_group.add(
            ScrapComponent(
                'comment', 
                symbol='c',
                info='A user submitted comment to a particular post.'
            )
        )

        # Add options to the 'post' component.
        p = component_group.get('post')
        p.add_option(
            'title', ValueType.STRING_COMPARISON, symbol='t',
            info='The title of the post.'
        )
        p.add_option(
            'score', ValueType.INT_RANGE, symbol='s',
            info='The score of the post (i.e. upvotes/downvotes).'
        )
        p.add_option('subreddit', ValueType.STRING_COMPARISON, symbol='r')
        p.add_option(
            'allow-subreddit', ValueType.LIST, symbol='A',
            info='Specify which subreddit(s) allowed to be scraped.'
        )
        p.add_option(
            'block-subreddit', ValueType.LIST, symbol='B',
            info='Specify which subreddit(s) not allowed to be scraped.'
        )

        # Add options to the 'comment' component.
        c = component_group.get('comment')
        c.add_option('text', ValueType.STRING_COMPARISON, symbol='t')
        c.add_option('score', ValueType.INT_RANGE, symbol='s')

    def setup_input(self, spider_input):
        spider_input.add_input(
            Input(
                'scan-subreddit', 
                InputType.STRING, 
                default='all',
                symbol='r',
                info='A comma separated list of subreddits to be scanned.'
            )
        )

        spider_input.add_input(
            Input(
                'limit', 
                InputType.INTEGER, 
                default=None,
                symbol='l',
                info='The limit on how many posts will be scanned.'
            )
        )

    def start(self):
        ##################################################
        # Initialize PRAW
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
        # Do spidery deeds.
        ##################################################
        p = self.component_group.get('post')
        counter  = 0

        # The limit on the number of items to be scanned.
        limit = self.spider_input.get('limit').val()
        logging.info('limit: %s' % limit)

        # Subreddits to be scanned.
        scan_subs = self.spider_input.get('scan-subreddit').val()
        scan_subs = '+'.join(scan_subs.split(','))
        logging.info('scan subreddits: %s' % scan_subs)

        # ListingGenerator of each sections.
        hot_section = self.r.subreddit(scan_subs).hot(limit=limit)
        new_section = self.r.subreddit(scan_subs).new(limit=limit)
        rising_section = self.r.subreddit(scan_subs).rising(limit=limit)
        top_section = self.r.subreddit(scan_subs).top(limit=limit)
        gilded_section = self.r.subreddit(scan_subs).gilded(limit=limit)

        all_sections = chain(hot_section, new_section, rising_section,
                             top_section, gilded_section)

        for post in all_sections:
            if p.get('subreddit').should_scrap(str(post.subreddit)) and\
               p.get('score').should_scrap(str(post.score)):
                counter += 1
                print('--------------------')
                print('ENTRY:', counter)
                print('TITLE:', post.title)
                print('SUBRE:', post.subreddit)
                print('SCORE:', post.score)

