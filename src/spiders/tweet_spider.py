import time
import tweepy
import re
import os
import platform
import logging

from dmine import Spider, ComponentLoader

#   Simple Twitter spider using Tweepy API
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
        sf_tweet.add('retweet_count', info='The retweets of the tweet')
        sf_tweet.add('fav_count',  info='The likes of the tweet')
        sf_tweet.add('replies_count', info='Replies of the tweet')

        # Attributes on replies / comments [WIP]
        sf_replies = sf.get('replies')
        sf_replies.add('retweet_count', info='The retweets of the comment')
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
        for trend in trendings:
            keyword=trend
            while True:
                try:
                    new_tweets = api.search(q=keyword, lang=sf.ret('lang'), count=100, result_type=sf.ret('tweet_type'), max_id=str(last_id - 1)) #max results per page
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

            #yield replies if skip_replies set to False and replies count not 0
            if not sf.ret('skip_replies') and int(replies_count) > 0:
                #self.mentions_replies( api, tag_name, tweet_id, sf, reply_count)
                sf_replies=sf.get('replies')
                max_id = None
                while True:
                    try:
                        replies =api.search(q="to:%s" % tag_name, since_id=int(tweet_id), max_id=max_id,rpp=100, count=1500)
                    except twitter.error.TwitterError as e:
                        logging.error("caught twitter api error: %s", e)
                        time.sleep(60)
                        continue
                    for reply in replies:
                        print(":O")
                        if reply.in_reply_to_status_id == tweet_id:

                            counts=api.get_status(tweet_id)
                            replies_count =counts.retweet_count
                            fav_count =counts.favorite_count

                            sf_replies.set_attr_values(
                                     author= reply.user.screen_name,
                                     retweet_count=reply.retweet_count,
                                     likes=fav_count,
                                     body=reply.text,
                                     replies_count=replies_count
                            )

                            if sf_replies.should_scrape():
                                yield ComponentLoader('replies', {'reply_id' :reply.id,
                                                                  'author' : reply.user.screen_name,
                                                                  'body' : reply.text,
                                                                  'retweet_count' : reply.retweet_count,
                                                                  'replies_count':replies_count,
                                                                  'likes' : reply.favorite_count
                                                                 })

                            # recursive magic to also get the replies to this reply
                            for reply_to_reply in get_replies(reply):
                                yield reply_to_reply
                                max_id = reply.id

                    if len(replies) != 100:
                        break

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

    def mentions_replies(self, api, tag_name, tweet_id, sf, reply_count):
        last_id = -1
        i=0
        flag = False
        while True:
            try:
                new_tweets=api.search(q="to:"+tag_name, since_id=int(tweet_id), rpp=1, count=1, max_id=str(last_id - 1))
                if not new_tweets:
                    break
                for tweet in new_tweets:
                    if tweet.in_reply_to_status_id_str == str(tweet_id):
                        print("found a reply")
                        i+=1
                last_id = new_tweets[-1].id

            except tweepy.TweepError as e:
                break
        print(i, reply_count)
