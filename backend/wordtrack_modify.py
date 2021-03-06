# -*- coding: utf-8 -*-
"""
Created on Fri Dec 14 03:58:46 2018

@author: khalid
"""


import pandas as pd
import numpy as np
from collections import Counter
import tweepy
#from sklearn.metrics.pairwise import cosine_similarity
#from sklearn.feature_extraction.text import TfidfVectorizer

consumer_key = "uQjxZTBtwpKJlJUjBTkKzZoOB"
consumer_secret = "DrHlZhHbylLUg25q7Inta7VL0TFTWEdufTpi8JIfo9nv3zUlec"
access_token =  "823320430702379009-aZzdJfrM03l7yslxR0h8xXJQKOUyaZC"
access_token_secret = "BYLJ36d7n0xr7VMPvfd9BOAeVQRoylueXbNf4vZ4Z16vT"
auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)
api = tweepy.API(auth)


class Wordtrack:
    
    def __init__(self,query,api=api,tweets_count=1000):
        self.query = query
#        self.tweets_count = tweets_count
        self.max_id = None
        self.api = api
        self.tweets = self.search(tweets_count/100)
#        self.gender()
        
    def search(self,iterr_num=1):
        """
        gather tweets
        pram : num of itteration
        return list of json objects
        """
        tweets=[]
        while iterr_num:
            try:
                tweets.extend(api.search(lang="en",q=self.query,count=100,result_type="mixed",include_rts = False, tweet_mode = 'extended',max_id=self.max_id))
                self.max_id = tweets[-1].id - 300000000000000 #day by day
                iterr_num-=1
            except :
                break
        return tweets
    
    
    
    
    def analysis(self):
        """
        analysis: create dataframe for tweets
        Parameter: None
        Return: json object
        """
        
        self.track_df = pd.DataFrame()
        hash_num = Counter()
        app = Counter()
        content = Counter()
        tweet_type = Counter()
        from_khalid_to_ghazy={}
        from_khalid_to_ghazy['timeline'] = []
        from_khalid_to_ghazy['analysis']=[]            

        
        for i,tweet in enumerate(self.tweets):
            if i == 20:
                break
            retweet_count=0
            self.track_df.loc[i,'created_at'] = tweet.created_at
            self.track_df.loc[i,'tweet'] = tweet.full_text
                        
            entity = tweet.entities            
            url = entity['urls']
            if entity.get('media'):
                media = entity.get('media')[0]
                contentv = media['type'] 
            elif len(url):
                contentv = 'url'
            else:
                contentv = 'text'
            
            if tweet.place==None:
                location = None
            else:
                location = tweet.place.country    

            
#                retweets                
            try:
                if tweet.retweeted_status:
                    retflag = True
            except:
                retflag = False

            if (retflag) and ( not (tweet.is_quote_status)) :
                typev ='retweet'
                
#                quote
            elif (tweet.is_quote_status) and  ( not (retflag)):
                typev ='quote'
                retweet_count+=tweet.retweet_count

#                reply                
            elif tweet.in_reply_to_user_id:
                typev ='reply'
                retweet_count+=tweet.retweet_count                

#                    orignal tweet
            else:
                typev ='tweet'
                retweet_count+=tweet.retweet_count                

            
            from_khalid_to_ghazy['timeline'].append({"name":tweet.user.name,
                        "user_url" : 'https://twitter.com/{}'.format(tweet.user.screen_name) ,
                        "user_pic" : tweet.user.profile_image_url,
                        "user_followers" : tweet.user.followers_count,
                        "user_type" : tweet.metadata['result_type'], #POPULAR OR RECENT
                        "tweet" : tweet.full_text,
                        "tweet_url" : "https://twitter.com/statuses/{}".format(tweet.id_str),
                        "likes" : tweet.favorite_count,
                        "retweet_count" : retweet_count,
                        "application" : tweet.source,
                        "created_at" : str(tweet.created_at),
                        "content" : contentv,
                        "location" : location
                        })
            
            app[tweet.source] += 1
            content[contentv] += 1
            tweet_type[typev] += 1
    
            hasht = tweet.entities['hashtags']
            for i in range(len(hasht)):
                hash_num[hasht[i]['text']] += 1

#            self.track_df.loc[i,'gender'] = self.gender_predict(tweet.user.name.lower())
            
           
        from_khalid_to_ghazy['analysis'].append({"freq_tweet_app" : dict(app),#.most_common(5),
                            "freq_tweet_content" : dict(content),
                            "freq_tweet_type" : dict(tweet_type),
                            "freq_tweet_hashtag" : dict(hash_num)
                            })
    
        
        return from_khalid_to_ghazy
    
    
    
# =============================================================================
#     
#     def extrainfo(self):
#         """
#         extrainfo: extra information about user like "engagement, gender, most freq applications, most mention users, day of week, type of tweets and the content"
#         Parameter: None
#         Return: ??
#         """
#         
#         self.preanalysis()
#         
#         self.day_of_week = self.track_df['created_at'].dt.day_name()
#         
# =============================================================================
        
# =============================================================================
#     
#     def gender(self):
#         self.gender_df = pd.read_csv(r"/project/datasets/name_gender.csv")
#         self.gender_df['name'] = self.gender_df['name'].str.lower()
#         self.gender_df.dropna(inplace=True)
#         self.tfidf_vectorizer = TfidfVectorizer()
#         self.tfidf_matrix = self.tfidf_vectorizer.fit_transform(self.gender_df['name'])
# 
#     def gender_predict(self,name):
#         
#         g = self.gender_df.loc[self.gender_df['name']==name,'gender']
#         
#         if len(g):
#             g.reset_index(drop=True,inplace=True)
#             return g[0]
#         else:
#             name = self.tfidf_vectorizer.transform([name])
#             self.out = cosine_similarity(name, self.tfidf_matrix)[0]
#             g = self.gender_df.loc[self.out.argmax(),'gender']
#             return g
# 
# 
# =============================================================================
    



# =============================================================================
#     
# ## Twitter credentials
# consumer_key = "uQjxZTBtwpKJlJUjBTkKzZoOB"
# consumer_secret = "DrHlZhHbylLUg25q7Inta7VL0TFTWEdufTpi8JIfo9nv3zUlec"
# access_token =  "823320430702379009-aZzdJfrM03l7yslxR0h8xXJQKOUyaZC"
# access_token_secret = "BYLJ36d7n0xr7VMPvfd9BOAeVQRoylueXbNf4vZ4Z16vT"
# auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
# auth.set_access_token(access_token, access_token_secret)
# api = tweepy.API(auth)
# 
# =============================================================================
