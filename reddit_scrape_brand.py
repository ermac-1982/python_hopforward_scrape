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

from_date = time.mktime(datetime.datetime(2021, 1, 1).timetuple())
to_date = time.mktime(datetime.datetime(2021, 2, 1).timetuple())


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
'beermoney',
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

for sub in subs:
    hot_posts = reddit.subreddit(sub).new(limit=1000)
    for post in hot_posts:
        for beer in brand_list:
            #print(beer)
            #print(post.title)
            if beer.casefold() in post.title.casefold():
               found_beers.append(beer)

               headlineslist.append(tuple([beer.casefold(),post.title]))
               #display.clear_output()


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


#send to database
execute_query = """insert into hop.beer_brand_tally_sent(brand, neg, neu, pos,compound, volume)
                values (?, ?, ?, ?, ?, ?)"""

cursor.executemany(execute_query,tally_sentiment.values.tolist())
myconnection.commit()

print(tally_sentiment)
#df = pd.DataFrame.from_records(results)
#df.head()




#print(found_beers)

# get hottest posts from all subreddits
#hot_posts = reddit.subreddit('all').hot(limit=10)
#for post in hot_posts:
#    print(post.title)

# iterate through top 10 hot posts and put info on a table
#posts = []
#ml_subreddit = reddit.subreddit('MachineLearning')
#for post in ml_subreddit.hot(limit=10):
#    posts.append([post.title, post.score, post.id, post.subreddit, post.url, post.num_comments, post.selftext, post.created])
#posts = pd.DataFrame(posts,columns=['title', 'score', 'id', 'subreddit', 'url', 'num_comments', 'body', 'created'])
#print(posts)

#Get comments from a post

#submission = reddit.submission(id="a3p0uq")

#for top_level_comment in submission.comments:
 #   print(top_level_comment.body)

#There get rid of the MoreComments objects, we can check the datatype of each comment before printing the body.

#for top_level_comment in submission.comments:
#    if isinstance(top_level_comment, MoreComments):
#        continue
#    print(top_level_comment.body)

posts = reddit.subreddit('wallstreetbets')
resp = posts.search('GME MEGATHREAD', limit=100)

for post in resp:
    #print(post.id)
    #postid = post.id
    submission = reddit.submission(id=post.id)
    for top_level_comment in submission.comments:
        if isinstance(top_level_comment, MoreComments):
            continue
        if top_level_comment.body.startswith("Jim Cramer"):
            if "\n" not in top_level_comment.body:
                print(top_level_comment.body)
