import tweepy as tw
import pandas as pd 
import datetime
import psycopg2
import re
from datetime import timedelta, datetime

'''db configuration'''
def get_db_connection():
    conn = psycopg2.connect(
        host="localhost",
        database="flask_db",
        user='postgres',
        password='password')
    return conn

'''fetching twitter API and insert into database'''
def fetch_data():
    api_key="rje6cf6oiSh86DnSBisOzv9a3"
    api_secret_key="5Q3eD834uEO36ojDEPaDfHOqnK4gkb86cNQjOSBiVg1e69m7fd"
    #authentication
    auth=tw.OAuthHandler(api_key,api_secret_key)
    api = tw.API(auth, wait_on_rate_limit=True)
    search_query = "#iphone14 -filter:retweets"
    # get tweets from the API

    now = datetime.today().now()
    prev=now-timedelta(days=1)
    now=now.strftime("%Y-%m-%d")
    prev=prev.strftime("%Y-%m-%d")

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM public.twitter_data ORDER BY tid DESC")
    last_data=cur.fetchone()
    last_id = lambda x : int(x) if x!= None else 0
    tweets = tw.Cursor(api.search_tweets,
                q=search_query,
                lang="en",
                since_id=last_id(last_data[4]),
                until=now).items(10)              

    # store the API responses in a list

    tweets_copy = []
    for tweet in tweets:
        # print("tweets are...",tweet)
        tweets_copy.append(tweet)
            
        
    print("Total Tweets fetched:", len(tweets_copy))

    #data convert to dataframe

    tweets_df=pd.DataFrame()

    # populate the dataframe
    for tweet in tweets_copy:
        hashtags = []
        try:
            for hashtag in tweet.entities["hashtags"]:
                hashtags.append(hashtag["text"])
            text = api.get_status(id=tweet.id, tweet_mode='extended').full_text
        except:
            pass
        tweets_df = tweets_df.append(pd.DataFrame({'user_name': tweet.user.name, 
                                                'user_location': tweet.user.location,\
                                                'user_description': tweet.user.description,
                                                'user_verified': tweet.user.verified,
                                                'date': tweet.created_at,
                                                'text': text, 
                                                'id':tweet.id,                                                
                                                'hashtags': [hashtags if hashtags else None],
                                                'source': tweet.source}))
        tweets_df = tweets_df.reset_index(drop=True)

    # ..................................Data description.............................................    

    if not tweets_df.empty:
        tweets_df_new=tweets_df.drop(['user_verified','user_location','user_description','hashtags','source'],axis=1)

    #.......................Twitter Data Cleaning............................................
    
        clean_tweets=[]

        for tweet in tweets_df_new['text']:
        
            tweet = re.sub("(@[A-Za-z0-9]+)|([^0-9A-Za-z \t])|(\w+:\/\/\S+)|([0-9])"," ",tweet)
            tweet= tweet.lower()   
            tweet=" ".join(tweet.split())  #to remove whitespaces btw text
            clean_tweets.append(tweet)
        tweets_df_new['text']=clean_tweets  

        conn = get_db_connection()
        cur = conn.cursor()
        for ind in tweets_df_new.index:
            cur.execute('INSERT INTO public.twitter_data (date, username, tweet_text,twitter_id)' 'VALUES(%s, %s, %s, %s)', (tweets_df_new['date'][ind],tweets_df_new['user_name'][ind],tweets_df_new['text'][ind], str(tweets_df_new['id'][ind])))
        conn.commit()
        cur.close()
        conn.close()

    return 'OK'