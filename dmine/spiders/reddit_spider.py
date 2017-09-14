#
# Reddit spider.
#
# Author(s): Amirul Menjeni, amirulmenjeni@gmail.com
#
# This spider will crawl the r/all subreddit, where all
# top posts from various subreddit are combined. There
# are many different options on how the posts can be
# listed. (e.g. list the posts that are top in past year, or 
# list the controversial post in past 24 hour). The spider
# is able to take in arguments specify the options.

# Available arguments:
#  category =
#      hot - look for posts that are placed in the hot section 
#            (front page).

#      new - look for posts that are posted recently
#            (most if not all will have 0 votes).

#      rising - look for posts that are trending.
#
#      controversial - look for posts that receive lots of downvotes.
#                      Time specification available.
#
#      top - look for posts that are the "top scoring links" on reddit.
#            Time specification available.
#  

import scrapy
import logging
import sys
import re

class RedditSpider(scrapy.Spider):
    name = 'reddit'
  
    # Process the category arguments.
    # Returns url(s) for start_urls depending on the categories selected.
    def get_start_urls(self):
        # Valid pattern for arg_category is cat1,cat2,cat3,...
        valid_pattern = r'\w+((,\w+)?)+'
        if not len(re.match(valid_pattern, self.arg_category)[0]) ==\
               len(self.arg_category):
            logging.error('Invalid pattern for arg_category spider argument. \
                           Valid example: category1, category2,...')
            sys.exit()

        categories = self.arg_category.split(',')

        # List of valid categories.
        valid_categories = ['hot', 'new', 'rising', 'controversial',\
                            'top', 'gilded']

        # Create starting urls.
        urls = []
        for c in categories:
            if c not in valid_categories:
                categories.remove(c)
                continue
            if c == 'hot':
                c = ''
            urls.append('https://www.reddit.com/%s' % c)
        return urls

    def get_keywords(self):
        keywords = self.arg_keywords.split(',')
        return keywords

    def start_requests(self):
        urls = self.get_start_urls()
        keywords = self.get_keywords()
        for url in urls:
            yield scrapy.Request(url, callback=self.parse_posts,\
                    meta= {'keywords': keywords})

    def parse_posts(self, response):
        post_links = response.css('a.comments::attr(href)').extract()

        # Get into each post's comment section and then
        # parse each comments.
        for link in post_links:
            link = response.urljoin(link)
            yield scrapy.Request(
                    link, 
                    callback=self.parse_comments,
                    meta={ 'post_id': link.split('/')[-3] }
            )

        # Go to the next page, and repeat.
        next_link = response.css('a.next-button::attr(href)').extract_first()
        if next_link is None:
            next_link = response.urljoin(next_link)
            logging.info('No page to scrape. Program closing...')
        yield scrapy.Request(next_link, callback=self.parse_posts)

    def parse_comments(self, response):
        comment_objects = response.css('div.entry')
        post_points = response.css('div.score span.number::text')\
                .extract_first()

        try:
            post_comment_count = response.css('.panestack-title .title::text')\
                    .re(r'\d+')[0]
            post_percentage = response.css('div.score').re(r'\d+%')[0]
        except IndexError:
            post_comment_count = '0'
            post_percentage = '0%'
        
        # Parsing each comments.
        for comment_object in comment_objects:
            comment = comment_object.css('div.md p::text').extract_first()
            comment_points = comment_object.css('.score::attr(title)')\
                    .extract_first()

            yield {
                'post_id': response.meta['post_id'],
                'post_points': post_points,
                'post_percentage': post_percentage,
                'post_comment_count': post_comment_count,
                'comment': comment,
                'comment_points' : comment_points
            } 
