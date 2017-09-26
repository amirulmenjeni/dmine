#
# Author(s): Amirul Menjeni (amirulmenjeni@gmail.com)
#

import sys
import praw
import logging
from dmine import Spider, ScrapComponent, ValueType, Input, InputType,\
                  ComponentLoader
from itertools import chain

class RedditSpider(Spider):
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
        c.add_option('body', ValueType.STRING_COMPARISON, symbol='t',
                     info='The comment\'s body.')
        c.add_option('score', ValueType.INT_RANGE, symbol='s',
                     info='The comment\'s score')

    def setup_input(self, input_group):
        input_group.add_input(
            Input(
                'scan-subreddit', 
                InputType.STRING, 
                default='all',
                symbol='r',
                info='A comma separated list of subreddits to be scanned.'
            )
        )

        input_group.add_input(
            Input(
                'scan-limit', 
                InputType.INTEGER, 
                default=None,
                symbol='l',
                info='The limit on how many posts from each listings '\
                     '(i.e. hot, rising, etc.) will be scanned.'
            )
        )

        input_group.add_input(
             Input(
                'post-limit',
                InputType.INTEGER,
                default=999999,
                info='The limit on how many posts can be collected. '\
                     'The default is no limit.'
            )
        )

        input_group.add_input(
            Input(
                'comment-limit',
                InputType.INTEGER,
                default=999999,
                info='The limit on how many comments can be collected. '\
                     'The default is no limit.'
            )
        )

        input_group.add_input(
            Input(
                'sections',
                InputType.STRING,
                default='hot,rising,new,top',
                info='The section in which the submission appear. Valid '\
                     'selection is hot, rising, new, or top.'
            )
        )

    def start(self, com, inp):
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
        p = com.get('post')
        c = com.get('comment')
        counter  = 0

        # Get the sections from which the post appear in each
        # subreddit.
        sections = self.get_sections(inp)

        post_limit = inp.get('post-limit').val()
        comment_limit = inp.get('comment-limit').val()

        post_count = 0
        comment_count = 0
        for section in sections:
            for post in section:
                # Assign each scrap options its filter target.
                p.set_targets(**{
                    'title': post.title,
                    'score': post.score,
                    'subreddit': str(post.subreddit)
                })

                # Scrape the post if it pass the filter.
                if p.should_scrap():
                    post_count += 1
                    yield ComponentLoader('post', {
                        'post_count': post_count,
                        'post_id': post.id,
                        'title': post.title,
                        'subreddit': str(post.subreddit),
                        'score': post.score,
                        'author': str(post.author)
                    })

                # Scraping (most if not all) comments of each post.
                post.comments.replace_more(limit=0)
                for comment in post.comments.list():
                    c.set_targets(**{
                        'body': comment.body,
                        'score': comment.score
                    })

                    if c.should_scrap():
                        comment_count += 1
                        yield ComponentLoader('comment', {
                            'comment_count': comment_count,
                            'post_id': post.id,
                            'comment_id': comment.id,
                            'author': str(comment.author),
                            'body': comment.body,
                            'score': str(comment.score)
                        })

    # Get which section(s) to scrape the submissions from.
    def get_sections(self, inp):
        # Get the list of sections.
        section_list = inp.get('sections').val().split(',')
        section_list = [s.strip() for s in section_list]

        # Subreddits to be scanned.
        scan_subs = inp.get('scan-subreddit').val()
        scan_subs = '+'.join(scan_subs.split(','))

        limit = inp.get('scan-limit').val()

        # Chain the listing generators of each section
        # into one listing generator.
        selected_sections = None
        if 'hot' in section_list:
            hot_section = self.r.subreddit(scan_subs).hot(limit=limit)
            yield hot_section
        if 'new' in section_list:
            new_section = self.r.subreddit(scan_subs).new(limit=limit)
            yield new_section
        if 'rising' in section_list:
            rising_section = self.r.subreddit(scan_subs).rising(limit=limit)
            yield rising_section
        if 'top' in section_list:
            top_section = self.r.subreddit(scan_subs).top(limit=limit)
            yield top_section
