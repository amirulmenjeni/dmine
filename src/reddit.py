#
# Author(s): Amirul Menjeni (amirulmenjeni@gmail.com
#

import praw
import argparse

class RedditCrawler():
    r = None

    def __init__(self):
        client_id = 'j8vNY5xeqUemQg' # Acquired from www.reddit.com/prefs/apps
        client_secret = None
        redirect_uri = 'http://localhost:8080'
        user_agent='Mozilla/5.0'
    
        print('client_id: %s\nclient_secret: %s\nuser_agent: %s' %\
                (client_id, client_secret, user_agent))
    
        self.r = praw.Reddit(
                    client_id=client_id,
                    client_secret=client_secret,
                    redirect_uri=redirect_uri,
                    user_agent=user_agent
                )
        self.r.auth.url(['identity'], 'http://localhost:8080', implicit=True))

    def crawl(self):
        pass

    def print_help(self):
        help_string =\
                """
                Usage:
                    python reddit.py <options>

                options:
                    -f --filter <filter characters>
                        The input argument <filter characters> is a series of
                        alphabetical characters. The available characters for
                        <filter characters> are as follows:
                        
                        p: posts
                        c: comments
                        u: users

                        For example, with the argument -f pcu, dmine will 
                        collect all posts (p) in all front page sections from 
                        all subreddits. It will also scrape every comments (c) 
                        in every posts scraped, as well as every users (u) 
                        it see when scraping.

                        Every filter character have their own filter options
                        to allow a more flexible and advanced filtering method.
                        The following are the subfilter characters for each
                        filter character:

                        p: subreddit, age, max_score, min_score
                        c: subreddit, age, max_score, min_score, author
                        u: age, 
                """


