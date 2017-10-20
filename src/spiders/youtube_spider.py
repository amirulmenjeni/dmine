import os
import json
from dmine import Spider, ComponentLoader
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait

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

        sf.add_var('search_types', type=list, default=['video'], info='Search options [ video, channel, playlist ]')
        sf.add_Var('order_by', default='relevance', info= 'Available options: upload date, ratings, relevance, title[Resources are sorted alphabetically by title], videocount, viewcount')
        sf.add_var('limit_vid', default = '5', info='limit for scraped video')
        sf.add_var('limit_channel', default = '5', info='limit for scraped video')
        sf.add_var('limit_playlist', default = '5', info='limit for scraped video')
        sf.add_var('keyword', default='', info='keyword to be scanned')
        sf.add_var('skip_comments', default='True', info='Scan comments option')
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
            url = 'https://www.googleapis.com/youtube/v3/search?q={}&key={}&part=snippet&maxResults={}&type={}'.format(q, dev_key, types_dict[search_type], search_type)
            types_dict[search_type]=url #replace limit values with url

        return types_dict

    def search_by_vid(self, sf, url):
        self.driver.get(url)
        json_text = self.driver.find_element_by_tag_name('body').text
        json_data = json.loads(json_text)

        sf_vid=sf.get('video')

        total_results=json_data['pageInfo']['totalResults']
        i=1
        for result in json_data['items']:
            sf_vid.set_attr_values(
                    title= result['snippet']['title'],
                    description=result['snippet']['description'],
                    channel_author=result['snippet']['channelTitle'],
                    publishedAt=result['snippet']['publishedAt']
            )

            if sf_vid.should_scrape():
                yield ComponentLoader('group', { 'vid_id' : result['id']['videoId'],
                                                 'title' : result['snippet']['title'],
                                                 'description' : result['snippet']['description'],
                                                 'channel_author':result['snippet']['channelTitle'],
                                                 'publishedAt': result['snippet']['publishedAt'].split("T"),
                                                 'entry_out_of' :"{} out of {}".format(i, total_results)
                                                })
            i+=1



    def search_by_channel(self, sf, url):
        pass

    def search_by_playlist(self, sf, url):
        pass
