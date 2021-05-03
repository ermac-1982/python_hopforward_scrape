from IPython import display
import math
from pprint import pprint
import pandas as pd
import numpy as np
import nltk
import matplotlib.pyplot as plt
import seaborn as sns
import praw
from praw.models import MoreComments
from nltk.sentiment.vader import SentimentIntensityAnalyzer as SIA

sns.set(style='darkgrid', context='talk', palette='Dark2')
reddit = praw.Reddit(client_id='DxRCwrqNJbnM9Q', client_secret='dbveQKIycUkfVwpytk69EPIJCy1x-Q', user_agent='hopforward')

headlines = set()

for submission in reddit.subreddit('politics').new(limit=10):
    headlines.add(submission.title)
    display.clear_output()
    print(len(headlines))

sia = SIA()
results = []

for line in headlines:
    pol_score = sia.polarity_scores(line)
    pol_score['headline'] = line
    results.append(pol_score)

pprint(results[:3], width=100)

df = pd.DataFrame.from_records(results)
df.head()

df['label'] = 0
df.loc[df['compound'] > 0.2, 'label'] = 1
df.loc[df['compound'] < -0.2, 'label'] = -1
df.head()