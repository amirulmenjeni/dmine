#
# Author(s): Amirul Menjeni (amirulmenjeni@gmail.com)
#

import sys
import praw
import logging
from dmine import Spider, Input, InputType, ComponentLoader

class RedditSpider(Spider):
    r = None # Reddit praw instance.
    name = 'reddit'

    def setup_filter(self, sf):
        """
        Scrape filter needs to be set up here.
        """

        # Create components.
        sf.add('post', info='A user post or submission')
        sf.add('comment', info='A user comment with respect to a post.')

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

    def setup_input(self, input_group):
        input_group.add_input(
            Input(
                'scan-subreddit', 
                InputType.STRING, 
                default='all',
                symbol='r',
                info='A whitespace separated list of subreddits to be '
                     'scanned. '\
                     'By default, r/all will be scanned.'
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
                default='hot rising new top',
                info='The section in which the submission appear. Valid '\
                     'selection is hot, rising, new, or top.'
            )
        )

        input_group.add_input(
            Input(
                'skip-comments',
                InputType.BOOLEAN,
                default=False,
                info='Skip comments entirely. This means the spider will '\
                     'scan posts or submissions.'
            )
        )

    def start(self):

        """
        Starts the spider.
        """
        ##################################################
        # Get the scrape filter object of this spider.
        ##################################################
        sf = self.scrape_filter
        sf_post = sf.get('post')
        sf_comment = sf.get('comment')

        ##################################################
        # Get the scrape input object of this spider.
        ##################################################
        inp = self.input_group

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
        sections = self.get_sections(inp)

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

                # Scraping (most if not all) comments of each post.
#                post.comments.replace_more(limit=0)
#                for comment in post.comments.list():
#                    sf_comment.set_attr_values(
#                        body=comment.body,
#                        score=comment.score
#                    )
#
#                    if sf_comment.should_scrape():
#                        yield ComponentLoader('comment', {
#                            'comment_id': comment.id,
#                            'author': str(comment.author),
#                            'body': comment.body,
#                            'score': str(comment.score)
#                        })

    # Get which section(s) to scrape the submissions from.
    def get_sections(self, inp):
        # Get the list of sections.
        section_list = inp.get('sections').val().split()

        # Subreddits to be scanned.
        scan_subs = inp.get('scan-subreddit').val()
        scan_subs = '+'.join(scan_subs.split())

        # Chain the listing generators of each section
        # into one listing generator.
        selected_sections = None
        if 'hot' in section_list:
            hot_section = self.r.subreddit(scan_subs).hot(limit=None)
            yield hot_section
        if 'new' in section_list:
            new_section = self.r.subreddit(scan_subs).new(limit=None)
            yield new_section
        if 'rising' in section_list:
            rising_section = self.r.subreddit(scan_subs).rising(limit=None)
            yield rising_section
        if 'top' in section_list:
            top_section = self.r.subreddit(scan_subs).top(limit=None)
            yield top_section
