import os
import json
from dmine import Spider, ComponentLoader
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait

base_url = "https://www.googleapis.com/youtube/v3/"

class YoutubeSpider(Spider):
    name = "youtube"

    def init(self, sf):
        self.driver = self.init_driver()

    def init_driver(self):
        path = os.path.join(os.getcwd(), 'dep-bin', 'phantomjs', 'bin', 'phantomjs')
        driver = webdriver.PhantomJS(executable_path=path)
        driver.wait = WebDriverWait(driver, 5)
        return driver

    def setup_filter(self, sf):
        sf.add_com('channel', info="Seaerch Keyword by channel name")
        sf.add_com('playlist', info="Seaerch Keyword by playlist titles")
        sf.add_com('video', info="Search Keyword by video titles")

        sf_vid=sf.get('video')
        sf_vid.add('publishedAt')
        sf_vid.add('title')
        sf_vid.add('description')
        sf_vid.add('channel_author')

        sf_channel=sf.get('channel')
        sf_channel.add('channel_name')
        sf_channel.add('description')
        sf_channel.add('date_created')
        sf_channel.add('country')


        sf.add_var('search_types', type=list, default=['channel'], info='Search options [ video, channel, playlist ]')
        sf.add_var('order_by', default='relevance', info= 'Available options: upload date, ratings, relevance, title[Resources are sorted alphabetically by title], videocount, viewcount')
        sf.add_var('limit_vid', type=int, default = '5', info='limit for scraped video')
        sf.add_var('limit_channel', type=int, default = '5', info='limit for scraped video')
        sf.add_var('limit_playlist', type=int, default = '5', info='limit for scraped video')
        sf.add_var('keyword', default='', info='keyword to be scanned')
        sf.add_var('skip_comments', type=bool, default='True', info='Scan comments option')
        if sf.ret('skip_comments'):
            sf_vid.add('limit_comment', default='20', info='Limit the number of comments scanned per video')
        sf.add_var('dev_key', default='AIzaSyCzsqDb0cxtKTcVDNZUU6mWbyPnAIRa0bs', info='Developer Key to access Youtube API')

    def start(self, sf):
        self.init(sf)
        url_list= self.construct_url(sf)
        types=sf.ret('search_types')
        func_dict = { 'video' : self.search_by_vid(sf, url_list['video']),
                       'channel' : self.search_by_channel(sf,  url_list['channel']),
                       'playlist' : self.search_by_playlist(sf,  url_list['playlist'])
                     }

        for search_type in types:
            for x in func_dict[search_type]:
                yield x

    def construct_url(self, sf):
        dev_key=sf.ret('dev_key')
        q=sf.ret('keyword')

        types_dict = { 'video' : sf.ret('limit_vid'),
                       'channel' : sf.ret('limit_channel'),
                       'playlist' : sf.ret('limit_channel')
                     }

        types=sf.ret('search_types')

        for search_type in types:
            if types_dict[search_type] > 50: #if limit is set to above 50 (Max resources returned per page is 50)
                 types_dict[search_type] = 50

            url = base_url + 'search?q={}&key={}&part=snippet&maxResults={}&type={}'.format(q, dev_key, types_dict[search_type], search_type)
            types_dict[search_type]=url #replace limit values with url

        return types_dict

    def get_category_tags(self, vid_id, dev_key):
        url=base_url+'videos?id={}&part=snippet&key={}'.format(vid_id, dev_key)
        self.driver.get(url)
        json_data=json.loads(self.driver.find_element_by_tag_name('body').text)
        tags=""
        if 'tags' in json_data['items'][0]['snippet']:
            tags=json_data['items'][0]['snippet']['tags']
        category_id=json_data['items'][0]['snippet']['categoryId']

        url=base_url+'videoCategories?id={}&part=snippet&key={}'.format(category_id, dev_key)
        self.driver.get(url)
        json_data=json.loads(self.driver.find_element_by_tag_name('body').text)
        category=json_data['items'][0]['snippet']['title']
        return tags, category

    def search_by_vid(self, sf, url):
        order_by=sf.ret('order_by')

        self.driver.get(url+"&order="+order_by)
        json_text = self.driver.find_element_by_tag_name('body').text
        json_data = json.loads(json_text)

        sf_vid=sf.get('video')
        dev_key=sf.ret('dev_key')
        total_results=json_data['pageInfo']['totalResults']

        i=1
        limit=sf.ret('limit_vid')
        page_token=""

        while i <= limit: #get resources until limit is reached

            for result in json_data['items']:
                if i > limit: return
                vid_id=result['id']['videoId']
                url_stats=base_url+'videos?part=statistics&id={}&key={}'.format(vid_id, dev_key)
                self.driver.get(url_stats)

                vid_stats=json.loads(self.driver.find_element_by_tag_name('body').text)
                stats = vid_stats['items'][0]['statistics']
                views=stats['viewCount']

                if 'likeCount' in stats:
                    likes=stats['likeCount']
                    dislikes=stats['dislikeCount']
                else:
                    likes, dislikes = 'Disabled', 'Disabled'

                comment=stats['commentCount']

                tags, category = self.get_category_tags(vid_id, dev_key)

                sf_vid.set_attr_values(
                        title= result['snippet']['title'],
                        description=result['snippet']['description'],
                        channel_author=result['snippet']['channelTitle'],
                        publishedAt=result['snippet']['publishedAt']
                )

                if sf_vid.should_scrape():
                    yield ComponentLoader('video', { 'vid_id' : result['id']['videoId'],
                                                     'entry_out_of' :"{} out of {}".format(i, total_results),
                                                     'title' : result['snippet']['title'],
                                                     'description' : result['snippet']['description'],
                                                     'channel_author':result['snippet']['channelTitle'],
                                                     'publishedAt': result['snippet']['publishedAt'].split("T"),
                                                     'views_count' : views,
                                                     'likes_count' : likes,
                                                     'dislike_count' : dislikes,
                                                     'comment_count' : comment,
                                                     'tags' : tags,
                                                     'category' : category
                                                    })
                i+=1

                if "nextPageToken" in json_data:
                    page_token=json_data['nextPageToken']
                else:
                    break

                url=url+"&pageToken="+page_token
                self.driver.get(url)
                json_text = self.driver.find_element_by_tag_name('body').text
                json_data = json.loads(json_text)

    def search_by_channel(self, sf, url):
        self.driver.get(url)
        json_data=json.loads(self.driver.find_element_by_tag_name('body').text)
        sf_channel=sf.get('channel')
        dev_key=sf.ret('dev_key')
        for channel in json_data['items']:
            channel_id=channel['id']['channelId']
            url_stats=base_url+'channels?part=statistics&id={}&key={}'.format(channel_id, dev_key)
            self.driver.get(url_stats)
            json_data=json.loads(self.driver.find_element_by_tag_name('body').text)

            stats=json_data['items'][0]['statistics']
            if not stats['hiddenSubscriberCount']:
                subscribers_count = stats['subscriberCount']
            else:
                subscribers_count = "hidden"
            video_count = stats['videoCount']
            views_count = stats['viewCount']

            url_stats=base_url+'channels?part=snippet&id={}&key={}'.format(channel_id, dev_key)
            self.driver.get(url_stats)
            json_data=json.loads(self.driver.find_element_by_tag_name('body').text)
            items=json_data['items'][0]['snippet']

            location=items['country'] if 'country' in items else "none"
            sf_channel.set_attr_values(
                    channel_name= channel['snippet']['title'],
                    description=channel['snippet']['description'],
                    date_created=channel['snippet']['publishedAt'],
                    country=location
            )

            if sf_channel.should_scrape():
                yield ComponentLoader('channel', { 'channel_id' : channel_id,
                                                   'channel_name' : channel['snippet']['title'],
                                                   'description' : channel['snippet']['description'],
                                                   'date_created' : channel['snippet']['publishedAt'],
                                                   'subscribers_count' : subscribers_count,
                                                   'video_count' : video_count,
                                                   'views_count' : views_count,
                                                   'country' : location
                                                })

    def search_by_playlist(self, sf, url):
        pass
