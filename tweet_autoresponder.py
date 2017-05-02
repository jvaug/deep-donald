from keys import keys

import json
import subprocess
import numpy as np
from time import sleep
import re

from tweepy.streaming import StreamListener
from tweepy import OAuthHandler
from tweepy import Stream
from tweepy import API

from sklearn.externals import joblib

model = joblib.load('lr_model.pkl')
tfidf = joblib.load('tfidf.pkl')

consumer_key = keys['consumer_key']
consumer_secret = keys['consumer_secret']
access_token = keys['access_token']
access_token_secret = keys['access_token_secret']
stream_rule = keys['stream_rule']
account_screen_name = keys['account_screen_name']
account_user_id = keys['account_user_id']
torch_rnn_path = keys['torch_rnn_path']
checkpoint_file_path = keys['checkpoint_file_path']

auth = OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)
twitterApi = API(auth)

class ReplyToTweet(StreamListener):

    def on_data(self, data):
        # print (data)
        print('Data Received')
        tweet = json.loads(data.strip())
        
        retweeted = tweet.get('retweeted')
        from_self = tweet.get('user',{}).get('id_str','') == account_user_id

        if retweeted is not None and not retweeted and not from_self:

            tweetId = tweet.get('id_str')
            screenName = tweet.get('user',{}).get('screen_name')
            tweetText = tweet.get('text')

            print('Tweet ID: ' + tweetId)
            print('From: ' + screenName)
            print('Tweet Text: ' + tweetText, '\n')
            
            bot_username_length = len(stream_rule)
            start_text_seed = tweetText[bot_username_length:]
            length = str(140 - len(start_text_seed))

            # 0.0 - 1.0, higher == more 'creative'
            temperature = str(0.6)

            # generate potential responses
            possible_responses = []

            for i in range(10):
                bash = ['th', 'sample.lua', '-checkpoint', checkpoint_file_path, '-length', length, '-temperature', temperature, '-start_text', start_text_seed, '-gpu', '-1']

                process = subprocess.run(bash, cwd=torch_rnn_path, stdout=subprocess.PIPE)
                # wait for bash output to finish
                sleep(4)

                chatResponse = str(process.stdout.decode('utf-8'))[:-len(screenName)]

                punctuation = ".!?"
                last_punc = 0

                for z, char in enumerate(chatResponse):
                    if char in punctuation:
                        last_punc = z+1

                final_response = re.sub( '\s+', ' ', chatResponse[:last_punc]).strip()
                possible_responses.append(final_response)
                print(i, final_response, '\n')


            predictions = model.predict_proba(tfidf.transform(np.array(possible_responses)))

            max_proba_index = 0
            max_proba = 0

            for b, x in enumerate(predictions):
                if x[1] > max_proba:
                    max_proba_index = b
                    max_proba = x[1]


            print('Index: ', max_proba_index)
            print('Max Proba: ', max_proba)
            print('Reponse: ',  possible_responses[max_proba_index], '\n')
            
            chatResponse = possible_responses[max_proba_index]

            replyText = '.@' + screenName + ' ' + chatResponse

            #check if response is over 140 char
            if len(replyText) > 140:
                replyText = replyText[0:139] + '…'

            
            print('Reply Text: ' + replyText)

            # If rate limited, the status posts should be queued up and sent on an interval
            # twitterApi.update_status(status=replyText, in_reply_to_status_id=tweetId)

    def on_error(self, status):
        print (status)

        # if rate limited, disconnect the stream
        if status == 420:
            return False


if __name__ == '__main__':
    streamListener = ReplyToTweet()
    twitterStream = Stream(auth, streamListener)
    twitterStream.userstream(_with='user')
