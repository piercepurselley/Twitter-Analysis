from tweepy import API
from tweepy import Cursor

from tweepy.streaming import StreamListener
from tweepy import OAuthHandler
from tweepy import Stream

from textblob import TextBlob
import re

import pandas as pd 
import numpy as np 
import matplotlib.pyplot as plt

import twitter_credentials

# # # AUTHENTICATER # # #
class  TwitterAuthenticater():
    def authenticate_twitter_app(self):
        auth = OAuthHandler(twitter_credentials.CONSUMER_KEY, twitter_credentials.CONSUMER_SECRET)
        auth.set_access_token(twitter_credentials.ACCESS_TOKEN,twitter_credentials.ACCESS_TOKEN_SECRET)
        return auth

# # # TWITTER CLIENT # # #  
class TwitterClient():
    """
    class for API client
    """
    def __init__(self,twitter_user=None):
        self.auth = TwitterAuthenticater().authenticate_twitter_app()
        self.twitter_client = API(self.auth)

        self.twitter_user = twitter_user

    def get_twitter_client_api(self):
        return self.twitter_client

    def get_user_timeline_tweets(self,num_tweets):
        tweets = []
        for tweet in Cursor(self.twitter_client.user_timeline, id=self.twitter_user).items(num_tweets):
            tweets.append(tweet)
        return tweets

    def get_friend_list(self,num_friends):
        friend_list = []
        for friend in Cursor(self.twitter_client.friends, id=self.twitter_user).items(num_friends):
            friend_list.append(friend)
        return friend_list

    def get_home_timeline_tweets(self,num_tweets):
        home_timeline_tweets = []
        for tweet in Cursor(self.twitter_client.home_timeline, id=self.twitter_user).items(num_tweets):
            home_timeline_tweets.append(tweet)
        return home_timeline_tweets


# # # STREAMER # # #
class TwitterStreamer():
    """
    class for streaming and processing live tweets
    """
    def __init__(self):
        self.twitter_authenticater = TwitterAuthenticater()

    def stream_tweets(self,fetched_tweets_filename,hash_tag_list):
        # Handles Twitter authentication and the connection to the Twitter Streaming API   
        listener = TwitterListener(fetched_tweets_filename)
        auth = self.twitter_authenticater.authenticate_twitter_app()
        stream = Stream(auth,listener)

        stream.filter(track=hash_tag_list)

# # # LISTENER # # #
class TwitterListener(StreamListener):
    """
    basic listener class
    """
    def __init__(self,fetched_tweets_filename):
        self.fetched_tweets_filename = fetched_tweets_filename

    def on_data(self,data):
        try:
            with open(self.fetched_tweets_filename, 'a') as tf:
                tf.write(data)
            return True 
        except BaseException as e:
            print("Error on data: %s" % str(e))
        return True

    def on_error(self,status):
        if status == 420:
            return False
        print(status)

class TweetAnalyzer():
    """
    analyzing and categorizing content from tweets
    """
    #removing special characters from the string, removing hyperlinks, and returning the cleaned tweet
    def clean_tweet(self, tweet):
        return ' '.join(re.sub("(@[A-Za-z0-9]+)|([^0-9A-Za-z \t])|(\w+:\/\/\S+)", " ", tweet).split())        
    
    def analyze_sentiment(self,tweet):
        analysis = TextBlob(self.clean_tweet(tweet))

        if analysis.sentiment.polarity > 0:
            return 1
        elif analysis.sentiment.polarity == 0:
            return 0
        else:
            return -1

    def tweets_to_dataframe(self,tweets):
        df = pd.DataFrame(data=[tweet.text for tweet in tweets],columns=['tweets'])

        df['id'] = np.array([tweet.id for tweet in tweets])
        df['len'] = np.array([len(tweet.text) for tweet in tweets])
        df['date'] = np.array([tweet.created_at for tweet in tweets])
        df['source'] = np.array([tweet.source for tweet in tweets])
        df['likes'] = np.array([tweet.favorite_count for tweet in tweets])
        df['retweets'] = np.array([tweet.retweet_count for tweet in tweets])

        return df


if __name__ == "__main__":
    
    twitter_client = TwitterClient()
    tweet_analyzer = TweetAnalyzer()
    api = twitter_client.get_twitter_client_api()

    tweets = api.user_timeline(screen_name="realdonaldtrump",count=200)

    #print(dir(tweets[0]))
    #print(tweets[0].id)
    #print(tweets[0].retweet_count)
    
    df = tweet_analyzer.tweets_to_dataframe(tweets)

    #adding sentiment column to dataframe
    df['sentiment'] = np.array([tweet_analyzer.analyze_sentiment(tweet) for tweet in df['tweets']])
    print(df.head(10))

    #get avg length over all tweets
    #print(np.mean(df['len']))

    #num of likes for most liked tweet
    #print(np.max(df['likes'])

    #num of retweets for most retweeted
    #print(np.max(df['retweets']))
    
    #hash_tag_list = ['sundance']
    #fetched_tweets_filename = "tweets.json"

    #twitter_client = TwitterClient('sundancefest')
    #print(twitter_client.get_user_timeline_tweets(2))

    #twitter_streamer = TwitterStreamer()
    #twitter_streamer.stream_tweets(fetched_tweets_filename,hash_tag_list)

    
    # # # # TIME SERIES # # # # 
    #time_likes = pd.Series(data=df['likes'].values, index=df['date'])
    #time_likes.plot(figsize=(16,4),color='r')
    #plt.show()

    #time_retweets = pd.Series(data=df['retweets'].values, index=df['date'])
    #time_retweets.plot(figsize=(16,4),color='r')
    #plt.show()

    #time_likes = pd.Series(data=df['likes'].values, index=df['date'])
    #time_likes.plot(figsize=(16,4),label='likes',legend=True)

    #time_retweets = pd.Series(data=df['retweets'].values, index=df['date'])
    #time_retweets.plot(figsize=(16,4),label='retweets',legend=True)
    #plt.show()