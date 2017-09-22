#
# Author(s): Amirul Menjeni (amirulmenjeni@gmail.com
#

import sys
import praw
import logging
from dmine_spider import DmineSpider
from scrap_filter import ScrapComponent, ScrapOption,\
                         Parser, ValueType, ComponentGroup

class RedditSpider(DmineSpider):
    r = None # Reddit prawl instance.
    name = 'reddit'

    def init(self):
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

    def setup_filter(self, component_group):
        # Add a scrap component called 'post'.
        component_group.add(ScrapComponent('post', symbol='p'))
        component_group.add(ScrapComponent('comment', symbol='c'))

        # Add options to the 'post' component.
        p = component_group.get('post')
        p.add_option('title', ValueType.STRING_COMPARISON, symbol='t')
        p.add_option('score', ValueType.INT_RANGE, symbol='s')
        p.add_option('subreddit', ValueType.STRING_COMPARISON, symbol='r')

        c = component_group.get('comment')
        c.add_option('text', ValueType.STRING_COMPARISON, symbol='t')
        c.add_option('score', ValueType.INT_RANGE, symbol='s')

    def start(self):
        # Example
        p = self.component_group.get('post')
        counter  = 0

        # Get each post/submission in r/all. Print 
        for post in self.r.subreddit('all').hot(limit=None):
            # If the filter is "p{/r:x == 'creepy'/s:0 < x <= 1000}",
            # only posts from r/creepy with score from 1 to 1000
            # will be printed out.
            if p.get('subreddit').should_scrap(str(post.subreddit)) and\
               p.get('score').should_scrap(str(post.score)):
                counter += 1
                print('--------------------')
                print('ENTRY:', counter)
                print('TITLE:', post.title)
                print('SUBRE:', post.subreddit)
                print('SCORE:', post.score)


