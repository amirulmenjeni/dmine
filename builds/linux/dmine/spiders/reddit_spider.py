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

    def comma_separated_list(value):
        if value is None:
            return value
        return [v.strip() for v in value.split(',')]

    def setup_filter(self, sf):
        """
        Scrape filter is REQUIRED to be set up here.
        """

        # Create components.
        sf.add_com('post', info='A user submission (also called as post).')
        sf.add_com('comment', info='A user comment reply to a submission.')
        sf.add_com('redditor', info='A redditor (also known as neckbeards).')

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
        sf_redditor.add('trophies', info='Trophies owned by the redditor.')

        # Create variables.
        sf.add_var(
            'subreddits',  default='all', 
            type=RedditSpider.comma_separated_list,
            info='The list of subreddits to scan, seperated by comma.'
        )
        sf.add_var(
            'sections', default='hot, rising, new, top',
            info='The section(s) where you want the spider to scan.'
        )
        sf.add_var(
            'skip_comments', default=False, type=bool,
            info='If this is set to True, comments will not be scanned '\
                 'for each scanned submission (post component).'
        )
        sf.add_var(
            'skip_redditors', default=True, type=bool,
            info='If this is set to True, redditors (redditor component) '\
                 'will not be scanned for each scanned '\
                 'comment (comment component) '
        )
        sf.add_var(
            'redditors', default=None, type=RedditSpider.comma_separated_list,
            info='A list of redditor usernames separated by comma. '\
                 'If there\'s at least one redditor set in this list, '\
                 'the spider will scan the redditor(s) instead of '\
                 'subreddit. Additionally, the @sections argument '\
                 'will be used to select the section(s) to scan the '\
                 'redditors\' submissions instead.'
        )

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
        sub_sections = self.get_subreddit_sections(
            sf.ret('sections'), sf.ret('subreddits')
        )

        # Get the sections from which the post/comment appear
        # in each redditor page.
        usr_sections = self.get_redditor_sections(
            sf.ret('sections'), sf.ret('redditors')
        )
        
        if not sf.ret('redditors'):
            for section in self.scrape_subreddits_sections(sf, sub_sections):
                yield section
        else:
            for redditor in self.scrape_redditors_sections(sf, usr_sections):
                yield redditor

    def scrape_subreddits_sections(self, sf, sections):
        """
        @param sf: ScrapeFilter of this spider.
        @param sections: A listing generator.

        Scrape each selected section(s) in the selected subreddit(s),
        given by the sections (generator) object.
        """
        for section in sections:
            for submission in self.scrape_submissions(sf, section):
                yield submission

    def scrape_submissions(self, sf, section):
        """
        @param sf: ScrapeFilter of this spider.
        @param section: A section object which contains post objects.

        Scrape each post from the given section.
        """
        sf_post = sf.get('post')
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

                if not sf.ret('skip_comments'):
                    for comment in self.scrape_comments(sf, post):
                        yield comment

    def scrape_comments(self, sf, post):
        """
        @param sf: ScrapeFilter of this spider.
        @param post: A post object which contains comment objects.
        """
        sf_comment = sf.get('comment')
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

                if not sf.ret('skip_redditors'):
                    usr_sections = self.get_redditor_sections(
                        sf.ret('sections'), [str(comment.author)]
                    )
                    for redditor in self.scrape_redditors_sections(
                        sf, usr_sections
                    ):
                        yield redditor 

    def scrape_redditors_sections(self, sf, sections):
        for section in sections:
            for item in self.scrape_redditors(sf, section):
                yield item

    def scrape_redditors(self, sf, section):
        for item in section:
            if isinstance(item, praw.models.Comment):
                yield ComponentLoader('comment', {
                    'comment_id': item.id,
                    'author': str(item.author),
                    'body': item.body,
                    'score': str(item.score)
                })
            elif isinstance(item, praw.models.Submission):
                yield ComponentLoader('post', {
                    'post_id': item.id,
                    'title': item.title,
                    'subreddit': str(item.subreddit),
                    'score': item.score,
                    'author': str(item.author)
                })

    def get_subreddit_sections(self, sections, scan_subs):
        """
        @param sections: The list of section(s) to select from.
        @param scan_subs: The list of subreddit(s) to scan.

        Get which section(s) in which subreddit(s) to scrape
        the submissions from. This method returns generator
        object of selected sections.
        """
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

    def get_redditor_sections(self, sections, scan_redditors):
        """
        @param sections: The list of section(s) to choose from.
        @param scan_redditors: The list of redditor(s) to scan.

        Get which section(s) in which redditor(s) to scrape
        the submissions and comments from. This method
        returns generator object of selected sections.
        """

        for username in scan_redditors:
            if 'hot' in sections:
                hot_section = self.r.redditor(username).hot()
                yield hot_section
            if 'new' in sections:
                new_section = self.r.redditor(username).new()
                yield new_section
            if 'top' in sections:
                top_section = self.r.redditor(username).top()
                yield top_section
