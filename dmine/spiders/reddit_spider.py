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
    def process_args(self):
        categories = self.arg_category.split(',')
        urls = []

        # Valid pattern for arg_category is cat1,cat2,cat3,..
        valid_pattern = r'\w+(,\w+)+'
        if not len(re.match(valid_pattern, self.arg_category)[0]) ==\
               len(self.arg_category):
            logging.error('Invalid pattern for arg_category spider argument. \
                           Valid example: category1, category2,...')
            sys.exit()

        # List of valid categories
        valid_categories = ['hot', 'new', 'rising', 'controversial',\
                            'top', 'gilded']

        for c in categories:
            if c not in valid_categories:
                categories.remove(c)
                continue
            if c == 'hot':
                c = ''
            urls.append('https://www.reddit.com/%s' % c)
        return urls

    def start_requests(self):
        urls = self.process_args()
        print('URLs:', urls)
        for url in urls:
            yield scrapy.Request(url, callback=self.parse)

    def parse(self, response):
        print(response.url)
        pass
