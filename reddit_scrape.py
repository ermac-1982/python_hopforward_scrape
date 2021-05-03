import praw
import pandas as pd
from praw.models import MoreComments
from seek_lists import beer_list
reddit = praw.Reddit(client_id='DxRCwrqNJbnM9Q', client_secret='dbveQKIycUkfVwpytk69EPIJCy1x-Q', user_agent='hopforward')
from collections import Counter
from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient
import os,uuid
import store
import database
import sys


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


# get 10 hot posts from the wallstreetbest subreddit

found_beers = []
beer_tally = []
beer_tally_name = ()
beer_tally_volume = ()

for sub in subs:
    hot_posts = reddit.subreddit(sub).hot(limit=1000)
    for post in hot_posts:
        for beer in beer_list:
            #print(beer)
            #print(post.title)
            if beer.casefold() in post.title.casefold():
               found_beers.append(beer)

for i in Counter(found_beers):
    beer_tally.append((i, Counter(found_beers)[i]))


execute_query = """insert into hop.beer_style_tally(style, volume)
                values (?, ?)"""

cursor.executemany(execute_query,beer_tally)
myconnection.commit()

print(beer_tally)





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
