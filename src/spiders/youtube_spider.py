import os
import json
import platform
from dmine import Spider, ComponentLoader, Project
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait

base_url = "https://www.googleapis.com/youtube/v3/"

class YoutubeSpider(Spider):
    name = "youtube"

    def __init__(self):
        self.driver = self.init_driver()

    def init_driver(self):
        path = Project.dep_bin_path
        if platform.uname().system == 'Linux':
            if platform.uname().machine == 'x86_64':
                path = os.path.join(path, 'phantomjs-2.1.1_linux_x86_64')
            elif platform.uname().machine == 'i686':
                path = os.path.join(path, 'phantomjs-2.1.1_linux_i686')
        elif platform.uname().system == 'Windows':
            path = os.path.join(path, 'phantomjs-2.1.1_windows.exe')
        else:
            msg = 'Unsupported platform: (%s, %s)'\
                  % (platform.system(), platform.machine())
            logging.error(msg)
            raise NotImplemented(msg)

        driver = webdriver.PhantomJS(executable_path=path)
        driver.wait = WebDriverWait(driver, 5)
        return driver

    def setup_filter(self, sf):
        sf.add_com('channel', info="Seaerch Keyword by channel name")
        sf.add_com('playlist', info="Seaerch Keyword by playlist titles")
        sf.add_com('video', info="Search Keyword by video titles")
        sf.add_com('comments', info="")

        sf_vid=sf.get('video')
        sf_vid.add('publishedAt')
        sf_vid.add('video_name')
        sf_vid.add('description')
        sf_vid.add('channel_author')

        sf_channel=sf.get('channel')
        sf_channel.add('channel_name')
        sf_channel.add('description')
        sf_channel.add('date_created')
        sf_channel.add('country')

        sf_playlist=sf.get('playlist')
        sf_playlist.add('playlist_name')
        sf_playlist.add('author_playlist')
        sf_playlist.add('date_created')
        sf_playlist.add('description')

        sf_comments=sf.get('comments')
        sf_comments.add('channel_author')
        sf_comments.add('body')
        sf_comments.add('like_count')
        sf_comments.add('reply_count')
        sf_comments.add('publishedAt')

        sf.add_var('search_types', type=list, default=['playlist'], info='Search options [ video, channel, playlist ]')
        sf.add_var('order_by', default='relevance', info= 'Available options: upload date, ratings, relevance, title[Resources are sorted alphabetically by title], videocount, viewcount')
        sf.add_var('keyword', default='', info='keyword to be scanned')
        sf.add_var('skip_comments', type=bool, default='True', info='Scan comments option')
        if sf.ret('skip_comments'):
            sf_vid.add('limit_comment', default='20', info='Limit the number of comments scanned per video')
        sf.add_var('dev_key', default='AIzaSyCzsqDb0cxtKTcVDNZUU6mWbyPnAIRa0bs', info='Developer Key to access Youtube API')

    def start(self, sf):
        url_list= self.construct_url(sf)
        types=sf.ret('search_types')

        if not sf.ret('keyword'): #if keyword not specified search by most popular vid on youtube
             for result in self.search_by_vid(sf, url_list):
                yield result
             return

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

        if not q : # Search by trending videos
            url = base_url + 'search?&key={}&part=snippet&chart=mostPopular&maxResults=50'.format(dev_key)
            return url

        types=sf.ret('search_types')
        types_dict={}

        for search_type in types:
            url = base_url + 'search?q={}&key={}&part=snippet&maxResults=50&type={}'.format(q, dev_key, search_type)
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

        page_token=""
        i=1
        while True: #get resources until limit is reached
            for result in json_data['items']:
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
                        video_name= result['snippet']['title'],
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

                if not sf.ret('skip_comments'):
                    for comment in self.fetch_comments(result['id']['videoId'], sf):
                        yield comment

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
        page_token=""

        while True: #get resources until limit is reached

            for channel in json_data['items']:
                channelID=channel['id']['channelId']

                url_stats=base_url+'channels?part=statistics&id={}&key={}'.format(channelID, dev_key)

                self.driver.get(url_stats)

                json_stats=json.loads(self.driver.find_element_by_tag_name('body').text)

                stats=json_stats['items'][0]['statistics']
                if not stats['hiddenSubscriberCount']:
                    subscribers_count = stats['subscriberCount']
                else:
                    subscribers_count = "hidden"
                video_count = stats['videoCount']
                views_count = stats['viewCount']

                url_stats=base_url+'channels?part=snippet&id={}&key={}'.format(channelID, dev_key)
                self.driver.get(url_stats)
                parsed_json=json.loads(self.driver.find_element_by_tag_name('body').text)
                items=parsed_json['items'][0]['snippet']

                location=items['country'] if 'country' in items else "none"
                sf_channel.set_attr_values(
                        channel_name= channel['snippet']['title'],
                        description=channel['snippet']['description'],
                        date_created=channel['snippet']['publishedAt'],
                        country=location
                )

                if sf_channel.should_scrape():
                    yield ComponentLoader('channel', { 'channel_id' : channelID,
                                                       'channel_name' : channel['snippet']['title'],
                                                       'description' : channel['snippet']['description'],
                                                       'date_created' : channel['snippet']['publishedAt'],
                                                       'subscribers_count' : subscribers_count,
                                                       'video_count' : video_count,
                                                       'views_count' : views_count,
                                                       'country' : location
                                                    })


                if "nextPageToken" in json_data:
                    page_token=json_data['nextPageToken']
                else:
                    flag=True
                    break

                url=url+"&pageToken="+page_token
                self.driver.get(url)
                json_text = self.driver.find_element_by_tag_name('body').text
                json_data = json.loads(json_text)


    def fetch_comments(self, vid_id, sf):
        dev_key=sf.ret('dev_key')
        url=base_url+"commentThreads?part=snippet&videoId={}&key={}&maxResults=50".format(vid_id, dev_key)
        self.driver.get(url)
        json_data=json.loads(self.driver.find_element_by_tag_name('body').text)
        sf_comments=sf.get('comments')

        total_results=json_data['pageInfo']['totalResults']
        page_token=""

        while True: #get resources until limit is reached
            for comment in json_data['items']:
                reply_count=comment['snippet']['totalReplyCount']
                is_public = comment['snippet']['isPublic']
                canReply= comment['snippet']['canReply']
                sf_comments.set_attr_values(
                        channel_author= comment['snippet']['topLevelComment']['snippet']['authorDisplayName'],
                        body=comment['snippet']['topLevelComment']['snippet']['textDisplay'],
                        like_count=comment['snippet']['topLevelComment']['snippet']['likeCount'],
                        reply_count=comment['snippet']['totalReplyCount'],
                        publishedAt=comment['snippet']['topLevelComment']['snippet']['publishedAt']
                )

                if sf_comments.should_scrape():
                    yield ComponentLoader('comments', { 'comment_id' : comment['snippet']['topLevelComment']['id'],
                                                        'vid_id' :  comment['snippet']['videoId'],
                                                        'channel_author': comment['snippet']['topLevelComment']['snippet']['authorDisplayName'],
                                                        'body': comment['snippet']['topLevelComment']['snippet']['textDisplay'],
                                                        'like_count': comment['snippet']['topLevelComment']['snippet']['likeCount'],
                                                        'publishedAt' : comment['snippet']['topLevelComment']['snippet']['publishedAt'],
                                                        'reply_count' : reply_count,
                                                        'is_public' : is_public,
                                                        'canReply' : canReply
                                                        })

    def search_by_playlist(self, sf, url):
        self.driver.get(url)
        json_data=json.loads(self.driver.find_element_by_tag_name('body').text)
        sf_playlist=sf.get('playlist')
        dev_key=sf.ret('dev_key')
        total_results=json_data['pageInfo']['totalResults']

        i=1
        page_token=""
        while True: #get resources until limit is reached
            for playlist in json_data['items']:
                sf_playlist.set_attr_values(
                        playlist_name= playlist['snippet']['title'],
                        description=playlist['snippet']['description'],
                        date_created=playlist['snippet']['publishedAt'],
                        author_playlist=playlist['snippet']['channelTitle']
                )

                if sf_playlist.should_scrape():
                    yield ComponentLoader('playlist', { 'playlist_name' : playlist['snippet']['title'],
                                                        'description' : playlist['snippet']['description'],
                                                        'date_created' : playlist['snippet']['publishedAt'],
                                                        'author_playlist' : playlist['snippet']['channelTitle'],
                                                        'entry_out_of' : "{} of {}".format(i, total_results)
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
