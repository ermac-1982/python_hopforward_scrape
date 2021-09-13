import praw
import pandas as pd
from praw.models import MoreComments
from seek_lists import brand_list
reddit = praw.Reddit(client_id='DxRCwrqNJbnM9Q', client_secret='dbveQKIycUkfVwpytk69EPIJCy1x-Q', user_agent='hopforward')
from collections import Counter
from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient
import os,uuid
import store
import database
import sys

from IPython import display
import math
from pprint import pprint
import pandas as pd
import numpy as np
import nltk
import matplotlib.pyplot as plt
import seaborn as sns
from praw.models import MoreComments
from nltk.sentiment.vader import SentimentIntensityAnalyzer as SIA
import datetime
import time

#from_date = time.mktime(datetime.datetime(2021, 1, 1).timetuple())
#to_date = time.mktime(datetime.datetime(2021, 2, 1).timetuple())

datetime_object_start = datetime.date(2021, 8, 1)
datetime_object_end = datetime.date(2021, 8, 31)

myconnection = database.azure_db_connect()
cursor = myconnection.cursor()


subs = ['beer',
'beercirclejerk',
'Untappd',
'beerandpizza',
'drunkvapes',
'beerwithaview',
'beerporn',
'TheBrewery',
'CraftBeer',
'homebrew',
'homebrews']


# Tally up brand style mentions + Sentiment


found_beers = []
beer_tally = []
beer_tally_name = ()
beer_tally_volume = ()

sns.set(style='darkgrid', context='talk', palette='Dark2')
headlines = set()
headlineslist = []

hot_topics = []
controversial_topics = []

#get new posts

for sub in subs:
    hot_posts = reddit.subreddit(sub).new(limit=1000)
    for post in hot_posts:
        if datetime_object_start <= datetime.date.fromtimestamp(post.created) <= datetime_object_end:
            for beer in brand_list:
                if beer.casefold() in post.title.casefold():
                    found_beers.append(beer)
                    headlineslist.append(tuple([beer.casefold(),post.title]))
                


sia = SIA()
results = []
dfappend=pd.DataFrame()

for beer in brand_list:
    for style, titles in headlineslist:
        if style.casefold() == beer.casefold():
            headlines.add(titles)
            #print(titles)

    for line in headlines:
        pol_score = sia.polarity_scores(line)
        pol_score['headline'] = line
        results.append(pol_score)
    
    if results:
        df = pd.DataFrame.from_records(results)
        df['style'] = beer
        dfappend = dfappend.append(df)
        #df.head()
    headlines.clear()
    results.clear()

dfappend.head()

#get average score by beer style
dfappend=dfappend.groupby(['style']).mean()

#get the tally
for i in Counter(found_beers):
    beer_tally.append((i, Counter(found_beers)[i]))

df = pd.DataFrame.from_records(beer_tally)
df.columns=['style','vol']

#combine tally and sentiment
tally_sentiment = dfappend.merge(df, on='style', how='left')  
tally_sentiment['date'] = datetime_object_start 

#send to database
execute_query = """insert into hop.beer_brand_tally_sent(brand, neg, neu, pos,compound, volume, created_datetime)
                values (?, ?, ?, ?, ?, ?, ?)"""

cursor.executemany(execute_query,tally_sentiment.values.tolist())

myconnection.commit()

# POPULATE HOT POSTS AND CONTROVERSIAL POSTS

#get hot posts

for sub in subs:
    hot_posts = reddit.subreddit(sub).hot(limit=1000)
    for post in hot_posts:
        for beer in brand_list:
            #print(beer)
            #print(post.title)
            if beer.casefold() in post.title.casefold():
                hot_topics.append((beer, post.permalink, post.title))


#get controversial

for sub in subs:
    hot_posts = reddit.subreddit(sub).controversial(limit=1000)
    for post in hot_posts:
        for beer in brand_list:
            #print(beer)
            #print(post.title)
            if beer.casefold() in post.title.casefold():
                controversial_topics.append((beer, post.permalink, post.title))


hot_topics_query = """ insert into hop.beer_brand_hot_topics(brand, posturl, content) values (?, ?, ?)"""
cont_topics_query = """ insert into hop.beer_brand_cont_topics(brand, posturl, content) values (?, ?, ?)"""

cursor.execute("""delete from hop.beer_brand_hot_topics""")
cursor.execute("""delete from hop.beer_brand_cont_topics""")

cursor.executemany(hot_topics_query,hot_topics)
cursor.executemany(cont_topics_query,controversial_topics)

myconnection.commit()