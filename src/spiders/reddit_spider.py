#
# Author(s): Amirul Menjeni (amirulmenjeni@gmail.com)
#

import sys
import praw
import logging
from dmine import Spider, ComponentLoader

class RedditSpider(Spider):
    r = None # Reddit praw instance.
    name = 'reddit'

    def __type_list(value):
        return [v.strip() for v in value.split(',')]

    def setup_filter(self, sf):
        """
        Scrape filter is REQUIRED to be set up here.
        """

        # Create components.
        sf.add_com('post', info='A user post or submission')
        sf.add_com('comment', info='A user comment with respect to a post.')
        sf.add_com('redditor', info='A redditor')

        # Add post attributes.
        sf_post = sf.get('post')
        sf_post.add('score', info='The upvote/downvote score of the post.')
        sf_post.add('title', info='The title of the post.')
        sf_post.add('subreddit', 
                    info='The subreddit to which the post is uploaded.')
        sf_post.add('author', info='The redditor who posted this post.')

        # Add comment attributes.
        sf_comment = sf.get('comment')
        sf_comment.add('score', 
                       info='The upvote/downvote score of the comment.')
        sf_comment.add('body', info='The comment text body.')
        sf_comment.add('author', info='The redditor who posted this comment.')

        # Add redditor attributes.
        sf_redditor = sf.get('redditor')
        sf_redditor.add('username', info='The redditor\'s username.')
        sf_redditor.add('trophies')

        # Create variables.
        sf.add_var('subreddits', 
                   default='all', type=RedditSpider.__type_list,
                   info='The list of subreddits to scan, seperated by comma.')
        sf.add_var('sections', default='hot, rising, new, top',
                    info='Get submissions that only presents in this list.')
        sf.add_var('skip_comments', default=False, type=bool,
                   info='Skip comments for each scanned post if set to True.')
        sf.add_var('redditor', default=None, type=RedditSpider.__type_list,
                   info='A list of redditor usernames separated by comma. '\
                        'If there\'s at least one redditor set in this list, '\
                        'the spider will scan the redditor(s) instead of '\
                        'subreddit.')

    def start(self, sf):
        """
        Starts the spider.
        """
        ##################################################
        # Get the scrape filter object of this spider.
        ##################################################
        sf_post = sf.get('post')
        sf_comment = sf.get('comment')
        sf_scan_subs = sf.ret('subreddits')

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
        self.r.auth.url([], redirect_uri, implicit=False)
    
        ##################################################
        # Do spidery deeds.
        ##################################################

        # Get the sections from which the post appear in each
        # subreddit.
        sections = self.get_sections(sf.ret('sections'), sf.ret('subreddits'))

        for section in sections:
            for post in section:
                # Assign each component's attribute.
                sf_post.set_attr_values(
                    title=post.title,
                    score=int(post.score),
                    subreddit=str(post.subreddit),
                    author=str(post.author)
                )

                # Scrape the post if it pass the filter.
                if sf_post.should_scrape():
                    yield ComponentLoader('post', {
                        'post_id': post.id,
                        'title': post.title,
                        'subreddit': str(post.subreddit),
                        'score': post.score,
                        'author': str(post.author)
                    })

                if sf.ret('skip_comments'):
                    continue

                # Scraping (most if not all) comments of each post.
                post.comments.replace_more(limit=0)
                for comment in post.comments.list():
                    sf_comment.set_attr_values(
                        body=comment.body,
                        score=comment.score,
                        author=str(comment.author)
                    )

                    if sf_comment.should_scrape():
                        yield ComponentLoader('comment', {
                            'comment_id': comment.id,
                            'author': str(comment.author),
                            'body': comment.body,
                            'score': str(comment.score)
                        })

    # Get which section(s) to scrape the submissions from.
    def get_sections(self, sections, scan_subs):
        scan_subs = '+'.join(scan_subs)

        # Chain the listing generators of each section
        # into one listing generator.
        selected_sections = None
        if 'hot' in sections:
            hot_section = self.r.subreddit(scan_subs).hot(limit=None)
            yield hot_section
        if 'new' in sections:
            new_section = self.r.subreddit(scan_subs).new(limit=None)
            yield new_section
        if 'rising' in sections:
            rising_section = self.r.subreddit(scan_subs).rising(limit=None)
            yield rising_section
        if 'top' in sections:
            top_section = self.r.subreddit(scan_subs).top(limit=None)
            yield top_section
