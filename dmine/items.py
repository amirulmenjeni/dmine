# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy
from scrapy.loader.processors import MapCompose, TakeFirst

class DmineItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass

class RedditItem():
    class Post(scrapy.Item):
        post_id = scrapy.Field(output_processor=TakeFirst())
        url = scrapy.Field(output_processor=TakeFirst())
        points = scrapy.Field(output_processor=TakeFirst())
        perc_score = scrapy.Field(output_processor=TakeFirst())
        title = scrapy.Field(output_processor=TakeFirst())
        subreddit = scrapy.Field(output_processor=TakeFirst())
        datetime = scrapy.Field(output_processor=TakeFirst())
        author = scrapy.Field(output_processor=TakeFirst())

    class Comment(scrapy.Item):
        text = scrapy.Field(output_processor=TakeFirst())
        points = scrapy.Field(output_processor=TakeFirst())
        datetime = scrapy.Field(output_processor=TakeFirst())
        author = scrapy.Field(output_processor=TakeFirst())

class TwitterItem():
    pass

    
