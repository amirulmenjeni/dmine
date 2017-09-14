#
# Reddit spider.
#
# Author: Amirul Menjeni, amirulmenjeni@gmail.com
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

class RedditSpider(scrapy.Spider):
    name = 'reddit'
    
    def start_requests(self):
        

    def parse(self, response):
        pass
