import time
import tweepy
import re
import json
import os
import platform
import logging
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.keys import Keys
from dmine import Spider, ComponentLoader

#   Simple Twitter spider using Tweepy and Selenium
#   You will need to generate your own API keys before accessing the Twitter api
#   Guide on how this is done: https://auth0.com/docs/connections/social/twitter

class TweetSpider(Spider):
    name = 'twitter'

    def __init__(self):
        self.driver= self.init_driver()

    def init_driver(self):
        path = os.path.relpath('./dep-bin/')

        if platform.uname().system == 'Linux':
            if platform.uname().machine == 'x86_64':
                path = os.path.join(
                    path, 'phantomjs-2.1.1-linux-x86_64', 'bin', 'phantomjs'
                )
            elif platform.uname().machine == 'i686':
                path = os.path.join(
                    path, 'phantomjs-2.1.1-linux-i686', 'bin', 'phantomjs'
                )
        elif platform.uname().system == 'Windows':
            path = os.path.join(
                path, 'phantomjs-2.1.1-windows', 'bin', 'phantomjs'
            )
        else:
            msg = 'Unsupported platform: (%s, %s)'\
                  % (platform.system(), platform.machine())
            logging.error(msg)
            raise NotImplemented(msg)

        logging.info('Using phantomjs binary: %s', path)
        driver = webdriver.PhantomJS(executable_path=path)
        driver.wait = WebDriverWait(driver, 5)
        return driver

    def setup_filter(self, sf):
        sf.add_com('tweet', info="A Tweet post")
        sf.add_com('tweet_user', info="Twitter user")
        sf.add_com('replies', info="replies made to a respective tweet")

        # Attributes on Tweet post
        sf_tweet = sf.get('tweet')
        sf_tweet.add('author', info='author of the tweet')
        sf_tweet.add('lang', info='The language of the tweet post')
        sf_tweet.add('retweet_count', info='The retweets of the tweet')
        sf_tweet.add('likes_count',  info='The likes of the tweet')
        sf_tweet.add('replies_count', info='Replies of the tweet')

        # Attributes on replies / comments [WIP]
        sf_replies = sf.get('replies')
        sf_replies.add('retweets', info='The retweets of the comment')
        sf_replies.add('likes', info='The likes of the comment')
        sf_replies.add('body', info='The reply text body.')
        sf_replies.add('author', info='The user who posted')

        # Attributes on user
        sf_user = sf.get('tweet_user')
        sf_user.add('username', info='On screen name of user')
        sf_user.add('tag_name', info='Display name of user account // e.g @unique_name ')
        sf_user.add('location', info='Location of user')
        sf_user.add('isVerified', info='is a verified Twitter account?')
        sf_user.add('user_lang',info='Lang of user')
        sf_user.add('followers', info='No. of followers')
        sf_user.add('statuses_count', info='No. of tweets user has posted')

        # Create variables.
        #Line 64-68 is negliblle if you are not using your own Twitter account
        sf.add_var('access_token', default='914875844623044609-sBDRGtzpWvcxVxznEutXO06IcPwNDbM', info='Required Keys to access api ')
        sf.add_var('access_token_secret', default='PlDBngjOu06GS9Bgu0wkOoehkag0ivzRc8ZJo3M7XtgSp', info='Required Keys to access api ')
        sf.add_var('consumer_key', default='fX7byz3KYiiQvfbs6xuCdgYYt', info='Required Keys to access api ')
        sf.add_var('consumer_secret', default='vGU5FngxDAPkzIc42bXsTKo5kgNEAhh6MibLDUYr0f4ApnHrzM', info='Required Keys to access api ')

        sf.add_var('tweet_type', default='mixed', info='Tweet types to scan: recent, popular and mixed')
        sf.add_var('skip_replies', default=True, type=bool,info='Skip replies for each scanned tweet if set to True.')
        sf.add_var('skip_author_info', default=True, type=bool,info='Skip author info for each tweet')
        sf.add_var('keyword', default="", info='the keyword in the tweet')
        sf.add_var('lang', default="en", info='language of tweet')
        sf.add_var('replies_limit', default=0, info='limit on replies to be shown if exists')

    def remove_emojis(self, text):
        myre = re.compile(u'('
                            u'\ud83c[\udf00-\udfff]|'
                            u'\ud83d[\udc00-\ude4f\ude80-\udeff]|'
                            u'[\u2600-\u26FF\u2700-\u27BF])+',
                            re.UNICODE)
        return myre.sub('',text)

    def fetch_trendings(self, api):
        trends1 = api.trends_place(1) #get worldwide 50 trending tweet topics
        data = trends1[0]
        trends = data['trends']
        trends_list = [trend['name'] for trend in trends]
        return trends_list

    def start(self, sf):
        consumer_key=sf.ret('consumer_key')
        consumer_secret=sf.ret('consumer_secret')
        access_token=sf.ret('access_token')
        access_token_secret=sf.ret('access_token_secret')

        searched_tweets = []
        last_id = -1

        auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
        auth.set_access_token(access_token, access_token_secret)
        api = tweepy.API(auth)
        keyword = sf.ret('keyword')

        if not keyword:
            trendings=self.fetch_trendings(api)
            #for trend in trendings:
        for trend in trendings:
            keyword=trend
            while True:
                try:
                    new_tweets = api.search(q=keyword, lang=sf.ret('lang'), rrp=100, count=1500, result_type=sf.ret('tweet_type'), max_id=str(last_id - 1)) #max results per page
                    if not new_tweets:
                        break
                    for tweet in self.scrape_tweet(api, sf, new_tweets):
                        yield tweet
                    last_id = new_tweets[-1].id

                except tweepy.TweepError as e:
                    break

    def scrape_tweet(self, api, sf, searched_tweets):
        sf_tweet = sf.get('tweet')

        for x in searched_tweets:
            tag_name =  x.user.screen_name
            user_name = x.user.name
            tweet_id=x.id

            counts=api.get_status(tweet_id)
            replies_count =counts.retweet_count

            fav_count =counts.favorite_count

            sf_tweet.set_attr_values(
                     author=tag_name,
                     lang=x.lang,
                     retweet_count=x.retweet_count,
                     replies_count=replies_count,
                     likes_count=fav_count
            )

            if sf_tweet.should_scrape():
                yield ComponentLoader('tweet', {
                                                 'tweet_id' : int(tweet_id),
                                                 'author' : "@"+tag_name,
                                                 'username' : user_name,
                                                 'body' : str(x.text),
                                                 'lang': x.lang,
                                                 'Date created' : x.created_at.strftime("%T %B %d, %Y"),
                                                 'retweet' : int(x.retweet_count),
                                                 'replies' : replies_count,
                                                 'fav count' : int(fav_count)
                })

            #yield replies if skip_replies set to False and replies count not 0
            if not sf.ret('skip_replies') and replies_count != 0:
                for x in self.fetch_replies(self.driver, tag_name, tweet_id, sf):
                    yield x

            if sf.ret('skip_author_info'):
                continue

            sf_user=sf.get('tweet_user')

            sf_user.set_attr_values(
                            tag_name=str(x.user.screen_name),
                            username= self.remove_emojis(str(x.user.name)),
                            location=str(x.user.location),
                            followers=int(x.user.followers_count),
                            user_lang=str(x.user.lang),
                            statuses_count=int(x.user.statuses_count),
                            isVerified=bool(x.user.verified)
            )

            if sf_user.should_scrape():
                        yield ComponentLoader('tweet_user', {
                            'user_id' : int(x.user.id),
                            'tag_name' : x.user.screen_name,
                            'username' :  self.remove_emojis(x.user.name),
                            'location' :  str(x.user.location),
                            'user_lang' : x.user.lang,
                            'followers' : int(x.user.followers_count),
                            'statuses_count' : int(x.user.statuses_count),
                            'is_verified' : x.user.verified,
                        })

    def fetch_replies(self, driver, author_name, tweet_id, sf):
        sf_replies=sf.get('replies')
        self.driver.get("https://twitter.com/{}/status/{}".format(author_name, tweet_id))
        time.sleep(1)

        try:
            replies_div =self.driver.find_elements_by_xpath(".//div[@data-component-context='replies']")

            #check if all replies are loaded
            current_page_length = 0
            while True:
                replies_div[len(replies_div)-1].send_keys(Keys.PAGE_DOWN)
                time.sleep(0.5)
                prev = current_page_length
                current_page_length = self.driver.execute_script("return document.body.scrollHeight")
                if current_page_length == prev : #If page height is retained break loop // no more results
                    break

            replies_div =self.driver.find_elements_by_xpath("//div[@data-component-context='replies']")
        except:
            pass
        
        c_list=[]
        replies_div.pop(0)

        #Scrape replies
        for x in replies_div:
            tweet_id = x.get_attribute("data-tweet-id")
            contents = x.find_element_by_xpath(".//div[@class='js-tweet-text-container']")
            author = x.find_element_by_class_name("stream-item-header").text
            username=author.split(' ')[0]
            tag_name=author.split(' ')[1]
            date_created=x.find_element_by_xpath(".//a[@class='tweet-timestamp js-permalink js-nav js-tooltip']").get_attribute('title')
            replies_response=x.find_elements_by_xpath(".//div[@class='ProfileTweet-actionList js-actions']/div")

            reply_count= replies_response[0].text.split('\n')[0]
            if not reply_count.isdigit() : reply_count = 0

            retweet_count=replies_response[1].text.split('\n')
            if len(retweet_count) > 1:
                retweet_count = int(replies_response[1].text.split('\n')[1])
            else:
                retweet_count=0

            likes_count=replies_response[2].text.split('\n')
            if len(likes_count) == 2:
                likes_count = likes_count[1]
            else:
                likes_count=0

            #checks if img/gif div is present
            if len(contents.text) == 0:
                contents.find_element_by_xpath("//div[@class='AdaptiveMediaOuterContainer']")
                c_list.append("user replied with a gif/img file")
            else:
                c_list.append(contents)

            #set component here
            sf_replies.set_attr_values(
                    retweets= int(retweet_count),
                    likes=int(likes_count),
                    body = contents.text,
                    author= tag_name
            )

            if sf_replies.should_scrape():
                        yield ComponentLoader('replies', {
                                'reply_id': int(tweet_id),
                                'author' : tag_name,
                                'body' : self.remove_emojis(contents.text),
                                'retweets' : int(retweet_count),
                                'fav count' : int(likes_count)
                        })
