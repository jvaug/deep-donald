import pandas as pd
import numpy as np
import json
import nltk


from textblob import TextBlob, Word

list_of_dfs = []

for year in range(2009,2018):
	df = pd.read_json('~/sample-python-autoreply/realdonaldtrump/%s.json' % year)
	list_of_dfs.append(df)


df = pd.concat(list_of_dfs, axis=0)

df = df[df.source == 'Twitter for Android'].copy()

df = df.text.copy()

# print(df)
# print(df.source.value_counts())

df.apply(str)

# import string
# df.apply(string.strip("'"))

import csv
df.to_csv('trump_aggregate_tweets_android.txt', index=False, header=False)#, quoting=csv.QUOTE_NONE)

# tweets = df.text.str.cat(sep=' ')
# tweets = tweets.lower()

# import re
# text = re.sub(r'http\S+', '', tweets)



# text_file = open("trump_aggregate_tweets_android.txt", "w")
# text_file.write(text)
# text_file.close()

# np.savetxt('trump2009.txt', df['text'].values, fmt='%.4e')


# df.text.to_csv('trump2009.txt', header=None, index=None, sep=' ')