import time
import tweepy
from collections import defaultdict
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.keys import Keys
from dmine import Spider, ComponentLoader


#   Simple Twitter spider using Tweepy and Selenium 
#   You will need to generate your own API keys before accessing the Twitter api
#   Guide on this is done: https://auth0.com/docs/connections/social/twitter

access_token = "914875844623044609-sBDRGtzpWvcxVxznEutXO06IcPwNDbM"
access_token_secret = "PlDBngjOu06GS9Bgu0wkOoehkag0ivzRc8ZJo3M7XtgSp"
consumer_key = "fX7byz3KYiiQvfbs6xuCdgYYt"
consumer_secret = "vGU5FngxDAPkzIc42bXsTKo5kgNEAhh6MibLDUYr0f4ApnHrzM"

class Tweetspider(Spider):
    name = 'twitter'
    
    def __init__(self):
        auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
        auth.set_access_token(access_token, access_token_secret)
        self.api = tweepy.API(auth)
        self.driver= self.init_driver()
        
    def init_driver(self):
        driver = webdriver.PhantomJS(executable_path=r'C:\PhantomJs\bin\phantomjs\bin\phantomjs.exe')
        driver.wait = WebDriverWait(driver, 5)
        return driver

    def setup_filter(self, sf):
        sf.add_com('tweet', info="Tweet post")
        sf.add_com('tweet_user', info="Twitter user")
        sf.add_com('replies', info="replies made to respective tweets")

        # Attributes on Tweet post
        sf_tweet = sf.get('tweet')
        sf_tweet.add('author', info='author of the tweet')
        sf_tweet.add('lang', info='The language of the tweet post')
        sf_tweet.add('retweet_count', 
                       info='The retweets of the tweet')
        sf_tweet.add('likes_count',  info='The likes of the tweet')
        sf_tweet.add('replies_count', info='Replies of the tweet')


        """# Attributes on replies / comments [WIP]
        sf_replies = sf.get('replies')
        sf_replies.add('retweets', 
                       info='The retweets of the comment')
        sf_replies.add('likes', 
                       info='The likes of the comment')
        sf_replies.add('body', info='The reply text body.')
        sf_replies.add('author', info='The user who posted')
        """
        
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
        sf.add_var('skip_comments', default=True, type=bool,info='Skip comments for each scanned tweet if set to True.')
        sf.add_var('skip_author_info', default=True, type=bool,info='Skip author info for each tweet')
        sf.add_var('limit', default= 5, info='limit results to be shown')
        sf.add_var('before', default = time.strftime("%d/%m/%Y"), info='tweet posted before date | Format: YYYY/MM/DD') #Only works up to 7 days from the current date
        sf.add_var('keyword', default="", info='the keyword in the tweet')
        sf.add_var('lang', default="en", info='type of tweet')

    def start(self, sf):
        
        searched_tweets = self.scrape(sf)
        sf_tweet = sf.get('tweet')
        
        for x in searched_tweets:

            tag_name =  x.user.screen_name 
            user_name = x.user.name
            tweet_id=x.id
                        
            #store each comments on a list, append to comments_dict with their associate tweet id as key
            replies_count= self.fetch_replies(tag_name, tweet_id, sf)

            fav_count=self.fetch_fav()
            
            sf_tweet.set_attr_values(
                     author=tag_name,
                     lang=str(x.lang),
                     retweet_count=int(x.retweet_count),
                     replies_count=int(replies_count),
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
                                                 'likes' : fav_count
                })
                
            if sf.ret('skip_author_info'):
                continue
            
            self.get_author_info(x.user, sf) #why??


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
         
    def get_author_info(self, user, sf):
        sf_user=sf.get('tweet_user')
        
        sf_user.set_attr_values(
                        tag_name=str(user.screen_name),
                        user_name= str(self.encode(user.name)),
                        location=str(user.location),
                        followers=int(user.followers_count),
                        user_lang=str(user.lang),
                        statuses_count=int(user.statuses_count),
                        is_verified=bool(user.verified)        
        )
        
        if sf_user.should_scrape():
                    yield ComponentLoader('tweet_user', {
                        'user_id' : user.id,
                        'tag_name' : user.screen_name,
                        'username' :  self.encode(user.name),
                        'location' :  self.encode(user.location),
                        'user_lang' : user.lang,
                        'followers' : user.followers_count,
                        'statuses_count' : user.statuses_count,
                        'is_verified' : user.verified,
                    })
        
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
            replies_div =self.driver.find_elements_by_xpath("//div[@data-component-context='replies']")

            if len(replies_div) == 0: #No replies/comments
                return 0
                
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
        if sf.ret('skip_comments'): return len(replies_div) #returns the amount of replies for each tweet

        #TODO
        """
        c_list=[]
        #set component here

        for x in replies_div:

            #contents = comments.find_elements_by_xpath("//p[@class='TweetTextSize  js-tweet-text tweet-text']")
            
            c_list.append(x.text)

        return len(c_list)
        """
