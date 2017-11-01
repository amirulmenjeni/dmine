import time
import tweepy
import requests
import json
from bs4 import BeautifulSoup
import re
from dmine import Spider, ComponentLoader, Project

#   A Twitter spider using Tweepy API
#   You will need to generate your own API keys before accessing the Twitter api
#   Guide on how this is done: https://auth0.com/docs/connections/social/twitter

class TweetSpider(Spider):
    name = 'twitter'

    def setup_filter(self, sf):
        sf.add_com('tweet', info="A Tweet post")
        sf.add_com('tweet_user', info="Twitter user")
        sf.add_com('replies', info="replies made to a respective tweet")

        # Attributes on Tweet post
        sf_tweet = sf.get('tweet')
        sf_tweet.add('author', info='author of the tweet')
        sf_tweet.add('lang', info='The language of the tweet post')
        sf_tweet.add('retweet_count', info='no. of retweets')
        sf_tweet.add('fav_count',  info='no. of fav ')
        sf_tweet.add('replies_count', info='no. of replies made to the tweet')

        # Attributes on replies / comments [WIP]
        sf_replies = sf.get('replies')
        sf_replies.add('retweet_count', info='The retweets of the comment')
        sf_replies.add('fav_count', info='The no. of favs of the comment')
        sf_replies.add('replies_count', info='The retweets of the comment')
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
        #Line 64-68 is negligible if you are not using your own Twitter account
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

        auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
        auth.set_access_token(access_token, access_token_secret)
        api = tweepy.API(auth)
        keyword = sf.ret('keyword')

        if not keyword:
            trendings=self.fetch_trendings(api)
            for trend in trendings:
                keyword=trend
                #Load tweets up to limit
                yield from self.load_tweets(api, sf, keyword)
        else:
            yield from self.load_tweets(api, sf, keyword)



    def load_tweets(self, api, sf, keyword):
        last_id = -1

        while True:
            try:
                new_tweets = api.search(q=keyword, lang=sf.ret('lang'), count=100, result_type=sf.ret('tweet_type'), max_id=str(last_id - 1)) #max results per page
                if not new_tweets:
                    break
                yield from self.scrape_tweet(api, sf, new_tweets)
                last_id = new_tweets[-1].id

            except tweepy.TweepError as e:
                return

    def load_replies(self, sf, author, tweet_id):
        base_url="https://twitter.com/i/{}/conversation/{}?include_available_features=1&include_entities=1&max_position={}&reset_error_state=false"
        pos=None
        data_dict = {}
        i=0

        while True:
            data=requests.get(base_url.format(author, tweet_id, pos))

            try:
                json_data=json.loads(data.content)
            except ValueError:

                break
            parsed=BeautifulSoup(json_data['items_html'],  "lxml")

            if sf.ret('skip_replies'):
                reply_div=parsed.find("button", { "class":"ProfileTweet-actionButton js-actionButton js-actionReply"})
                reply_count=reply_div.find("span", {"class" : "ProfileTweet-actionCountForPresentation"}).text
                if reply_count == "":
                    reply_count=0
                return reply_count

            body=parsed.find_all("p", {"class":"TweetTextSize js-tweet-text tweet-text"})
            author=parsed.find_all("a", "account-group js-account-group js-action-profile js-user-profile-link js-nav")

            for i in range(1,len(author)):
                print(author[i].find("span","username u-dir").text, body[i].text)
            if not json_data['has_more_items']:
                break
            pos=json_data['min_position']



        """
        sf_replies.set_attr_values(
                 author= reply.user.screen_name,
                 retweet_count=reply.retweet_count,
                 fav_count=fav_count,
                 body=body,
                 replies_count=replies_count
        )

        if sf_replies.should_scrape():
            yield ComponentLoader('replies', {'reply_id' :reply.id,
                                              'author' : reply.user.screen_name,
                                              'body' : reply.text

                                             })
        yield from content
        """
    def load_status(self, author, tweet_id):
        ses = requests.Session()
        base_url="https://twitter.com/i/{}/conversation/{}?include_available_features=1&include_entities=1&max_position={}&reset_error_state=false"
        data=ses.get(base_url.format(author, tweet_id, None))

        try:
            json_data=json.loads(data.content)
        except ValueError:
            logging.info("..")
        parsed=BeautifulSoup(json_data['items_html'],  "lxml")
        try: #if twitter does not exist 
            reply_div=parsed.find("button", { "class":"ProfileTweet-actionButton js-actionButton js-actionReply"})
            reply_count=reply_div.find("span", {"class" : "ProfileTweet-actionCountForPresentation"}).text
        except:
            return 0, 0

        if reply_count == "":
            reply_count=0
        fav_div=parsed.find("button", { "class":"ProfileTweet-actionButton js-actionButton js-actionFavorite"})
        fav_count=fav_div.find("span", {"class" : "ProfileTweet-actionCountForPresentation"}).text
        if fav_count == "":
            fav_count=0
        return reply_count, fav_count

    def scrape_tweet(self, api, sf, searched_tweets):
        sf_tweet = sf.get('tweet')

        for x in searched_tweets:
            tag_name =  x.user.screen_name
            user_name = x.user.name
            tweet_id=x.id

            replies_count, fav_count=self.load_status(tag_name, tweet_id)

            sf_tweet.set_attr_values(
                     author=tag_name,
                     lang=x.lang,
                     retweet_count=x.retweet_count,
                     replies_count=replies_count,
                     fav_count=fav_count
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
                                                 'fav_count' : int(fav_count)
                })

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
                            'user_id' : int(x.user.id),
                            'tag_name' : x.user.screen_name,
                            'username' :  x.user.name,
                            'location' :  str(x.user.location),
                            'user_lang' : x.user.lang,
                            'followers' : int(x.user.followers_count),
                            'statuses_count' : int(x.user.statuses_count),
                            'is_verified' : x.user.verified,
                        })
