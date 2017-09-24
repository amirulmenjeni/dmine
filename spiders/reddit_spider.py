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
                'scan-limit', 
                InputType.INTEGER, 
                default=None,
                symbol='l',
                info='The limit on how many posts will be scanned.'
            )
        )

        spider_input.add_input(
            Input(
                'sections',
                InputType.STRING,
                default='hot,rising,new,top',
                info='The section in which the submission appear. Valid '\
                     'selection is hot, rising, new, or top.'
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

        # Get the sections from which the post appear in each
        # subreddit.
        sections = self.get_sections()

        for post in sections:
            # Scraping the posts.
            if p.get('subreddit').should_scrap(str(post.subreddit)) and\
               p.get('score').should_scrap(str(post.score)):

                yield {
                    'title': post.title,
                    'subreddit': str(post.subreddit),
                    'score': str(post.score),
                    'author': str(post.author)
                }

    def get_sections(self):
        # Get the list of sections.
        section_list = self.spider_input.get('sections').val().split(',')
        section_list = [s.strip() for s in section_list]

        # Subreddits to be scanned.
        scan_subs = self.spider_input.get('scan-subreddit').val()
        scan_subs = '+'.join(scan_subs.split(','))

        # Chain the listing generators of each section
        # into one listing generator.
        selected_sections = None
        if 'hot' in section_list:
            hot_section = self.r.subreddit(scan_subs).hot(limit=None)
            selected_sections = chain(hot_section)
        if 'new' in section_list:
            new_section = self.r.subreddit(scan_subs).new(limit=None)
            selected_sections = chain(new_section)
        if 'rising' in section_list:
            rising_section = self.r.subreddit(scan_subs).rising(limit=None)
            selected_sections = chain(rising_section)
        if 'top' in section_list:
            top_section = self.r.subreddit(scan_subs).top(limit=None)
            selected_sections = chain(top_section)
        return selected_sections


