import time
import tweepy
import os
import os
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.keys import Keys
from dmine import Spider, ComponentLoader

#   Simple Twitter spider using Tweepy and Selenium
#   You will need to generate your own API keys before accessing the Twitter api
#   Guide on how this is done: https://auth0.com/docs/connections/social/twitter

access_token = "914875844623044609-sBDRGtzpWvcxVxznEutXO06IcPwNDbM"
access_token_secret = "PlDBngjOu06GS9Bgu0wkOoehkag0ivzRc8ZJo3M7XtgSp"
consumer_key = "fX7byz3KYiiQvfbs6xuCdgYYt"
consumer_secret = "vGU5FngxDAPkzIc42bXsTKo5kgNEAhh6MibLDUYr0f4ApnHrzM"

class TweetSpider(Spider):
    name = 'twitter'

    def __init__(self):
        auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
        auth.set_access_token(access_token, access_token_secret)
        self.api = tweepy.API(auth)
        self.driver= self.init_driver()

    def init_driver(self):
        driver = webdriver.PhantomJS(executable_path=r'phantomjs\bin\phantomjs.exe')
        driver.wait = WebDriverWait(driver, 5)
        return driver

    def setup_filter(self, sf):
        sf.add_com('tweet', info="A Tweet post")
        sf.add_com('tweet_user', info="Twitter user")
        sf.add_com('replies', info="replies made to respective tweet")

        # Attributes on Tweet post
        sf_tweet = sf.get('tweet')
        sf_tweet.add('author', info='author of the tweet')
        sf_tweet.add('lang', info='The language of the tweet post')
        sf_tweet.add('retweet_count',
                       info='The retweets of the tweet')
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
        sf.add_var('tweet_type', default='mixed', info='Tweet types to scan: recent, popular and mixed')
        sf.add_var('skip_replies', default=True, type=bool,info='Skip replies for each scanned tweet if set to True.')
        sf.add_var('skip_author_info', default=True, type=bool,info='Skip author info for each tweet')
        sf.add_var('limit', default= 5, info='limit results to be shown')
        sf.add_var('before', default = time.strftime("%d/%m/%Y"), info='tweet posted before date | Format: YYYY/MM/DD') #Only works up to 7 days from the current date
        sf.add_var('keyword', default="", info='the keyword in the tweet')
        sf.add_var('lang', default="en", info='type of tweet')
        sf.add_var('replies_limit', default=0, info='limit on replies to be shown if exists')

    def start(self, sf):

        searched_tweets = self.scrape(sf)
        sf_tweet = sf.get('tweet')

        for x in searched_tweets:
            tag_name =  x.user.screen_name
            user_name = x.user.name
            tweet_id=x.id

            replies= self.fetch_replies(tag_name, tweet_id, sf)
            replies_count = next(replies)

            fav_count = self.fetch_fav()

            sf_tweet.set_attr_values(
                     author=tag_name,
                     lang=x.lang,
                     retweet_count=x.retweet_count,
                     replies_count=replies_count,
                     likes_count=fav_count
            )

            if sf_tweet.should_scrape():
                yield ComponentLoader('tweet', {
                                                 'Tweet id' : tweet_id,
                                                 'author' : "@"+tag_name,
                                                 'username' : user_name,
                                                 'body' : x.text,
                                                 'lang': x.lang,
                                                 'Date created' : x.created_at.strftime("%T %B %d, %Y"),
                                                 'retweet' : x.retweet_count,
                                                 'replies' : replies_count,
                                                 'fav count' : fav_count
                })

                #yield replies if skip_replies set to False
            #while True:
            #    yield next(replies)

            if sf.ret('skip_author_info'):
                continue

            sf_user=sf.get('tweet_user')

            sf_user.set_attr_values(
                            tag_name=str(x.user.screen_name),
                            username= str(x.user.name),
                            location=str(x.user.location),
                            followers=int(x.user.followers_count),
                            user_lang=str(x.user.lang),
                            statuses_count=int(x.user.statuses_count),
                            isVerified=bool(x.user.verified)
            )

            if sf_user.should_scrape():
                        yield ComponentLoader('tweet_user', {
                            'user_id' : x.user.id,
                            'tag_name' : x.user.screen_name,
                            'username' :  x.user.name,
                            'location' :  x.user.location,
                            'user_lang' : x.user.lang,
                            'followers' : x.user.followers_count,
                            'statuses_count' : x.user.statuses_count,
                            'is_verified' : x.user.verified,
                        })


    def scrape(self, sf):
        searched_tweets = []
        last_id = -1
        limit = int(sf.ret('limit'))
        #Get all tweet results up to limit

        while len(searched_tweets) < limit:
            count = limit - len(searched_tweets)

            try:
                new_tweets = self.api.search(q=sf.ret('keyword'), result_type=sf.ret('tweet_type'), count=limit, max_id=str(last_id - 1))
                if not new_tweets:
                    break
                searched_tweets.extend(new_tweets)
                last_id = new_tweets[-1].id

            except tweepy.TweepError as e:

                break

        return searched_tweets

    def fetch_fav(self):
        try:
            f=self.driver.find_element_by_xpath("//a[@class='request-favorited-popup']").get_attribute("data-activity-popup-title")
            f=int(f.split(' ')[0].replace(',', ''))
        except:
            f=0
        return f

    def fetch_replies(self, author_name, tweet_id, sf):
        sf_replies=sf.get('replies')
        self.driver.get("https://twitter.com/{}/status/{}".format(author_name, tweet_id))
        time.sleep(2)

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
            return 0

        if sf.ret('skip_replies'):
            yield len(replies_div) #returns the amount of replies for each tweet
        c_list=[]
        replies_div.pop(0)

        yield len(replies_div)

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
                    retweets= retweet_count,
                    likes=likes_count,
                    body = contents.text,
                    author= tag_name
            )

            if sf_replies.should_scrape():
                        yield ComponentLoader('replies', {
                                'reply id': tweet_id,
                                'author' : tag_name,
                                'body' : contents.text,
                                'retweets' : retweet_count,
                                'fav count' : likes_count
                        })
