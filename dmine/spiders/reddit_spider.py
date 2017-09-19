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
from scrapy.loader import ItemLoader
from dmine.items import RedditItem

class RedditSpider(scrapy.Spider):
    name = 'reddit'
    require_login = False
    post_data = []
    comm_data = []
  
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
    
        # Filter out any invalid categories.
        categories = self.arg_category.split(',')
        valid_categories = ['hot', 'new', 'rising', 'controversial',\
                            'top', 'gilded']
        categories = filter(lambda x: x in valid_categories, categories)

        # Create starting urls.
        urls = []
        for c in categories:
            if c not in valid_categories:
                categories.remove(c)
                continue
            # Gilded section requires login.
            if c == 'gilded':
                self.require_login = True
            # Hot category is the home page.
            if c == 'hot':
                c = ''
            urls.append('https://www.reddit.com/%s' % c)
        return urls

    def start_requests(self):
        urls = self.get_start_urls()
        for url in urls:
            yield scrapy.Request(url, callback=self.parse_posts)

    def parse_posts(self, response):
        post_ids = response.css('#siteTable .comments::attr(href)')\
                .re('\/comments\/(\w+)\/')
        il = ItemLoader(item=RedditItem.Post(), response=response)
        for i in post_ids:
            il.add_value('post_id', i)
            il.add_css('url', '#siteTable .comments::attr(href)')
            il.add_css('points', '.score.unvoted::attr(title)')
            il.add_css('title', '#siteTable a.title::text')
            il.add_css('subreddit', 'a.subreddit::text')
            il.add_css('datetime', 'time.live-timestamp::attr(datetime)')
            il.add_css('author', '.author::text')
        post_items = il.load_item()

        # Request the comment section of every posts and
        # parse away.
        for post in post_items:
            yield scrapy.Request(
                    post['url'] + '?limit=500', # Show max possible comments
                    callback=self.parse_comments,
                    meta={ 'post_id': post['post_id'] }
                  )

        yield post_items
    
        # Next page.
        next_url = response.css('.next-button a::attr(href)').extract_first()
        if next_url is None:
            logging.info('No more page to scrape. Program closing...')
        next_url = response.urljoin(next_url)
        yield scrapy.Request(next_url, callback=self.parse_posts)

#    def parse_comments(self, response):
#        comment_objects = response.css('div.entry')
#        post_id = response.css('#shortlink-text::attr(value)').extract_first()
#        post_id = post_id.split('/')[-1]
#        post_title = response.css('.outbound::text').extract_first()
#        post_points = response.css('div.score span.number::text')\
#                .extract_first()
#        try:
#            post_comment_count = response.css('.panestack-title .title::text')\
#                    .re(r'\d+')[0]
#            post_percentage = response.css('div.score').re(r'\d+%')[0]
#        except IndexError:
#            post_comment_count = '0'
#            post_percentage = '0%'
#        
#        # Parsing each comments.
#        for comment_object in comment_objects:
#            comment = comment_object.css('div.md p::text').extract_first()
#            comment_points = comment_object.css('.score::attr(title)')\
#                    .extract_first()
#            yield {
#                'post_id': post_id,
#                'post_title': post_title,
#                'post_points': post_points,
#                'post_percentage': post_percentage,
#                'post_comment_count': post_comment_count,
#                'comment': comment,
#                'comment_points' : comment_points
#            } 

    def parse_comments(self, response):
        il = ItemLoader(item=RedditItem.Comment(), response=response)
        pass

