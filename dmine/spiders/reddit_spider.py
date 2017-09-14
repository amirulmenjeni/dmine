#
# Reddit spider.
#
# Author: Amirul Menjeni, amirulmenjeni@gmail.com
# 

class RedditSpider(scrapy.Spider):
    name = 'reddit'
    start_urls = [
        'http://www.reddit.com'
    ]

    def parse(self, response):
        pass
