from keys import keys

import json
import subprocess
import numpy as np
from time import sleep
import re
import language_check

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

tool = language_check.LanguageTool('en-US')

class ReplyToTweet(StreamListener):

    def on_data(self, data):
        # print(data)
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
            temperature = str(0.45)

            # generate potential responses
            possible_responses = []

            for i in range(1,11):
                bash = ['th', 'sample.lua', '-checkpoint', checkpoint_file_path, '-length', length, '-temperature', temperature, '-start_text', start_text_seed, '-gpu', '-1']

                process = subprocess.run(bash, cwd=torch_rnn_path, stdout=subprocess.PIPE)
                # wait for bash output to finish
                sleep(2)

                chatResponse = str(process.stdout.decode('utf-8'))[:-len(screenName)]

                punctuation = ".!?"
                last_punc = 0

                for z, char in enumerate(chatResponse):
                    if char in punctuation:
                        last_punc = z+1

                final_response = re.sub( '\s+', ' ', chatResponse[:last_punc]).strip()

                print('Pre ', i, chatResponse, '\n')
                print('Trim', i, final_response, '\n')

                matches = tool.check(final_response)
                final_response = language_check.correct(final_response, matches)
                print('Post', i, final_response, '\n\n')

                possible_responses.append(final_response)

            predictions = model.predict_proba(tfidf.transform(np.array(possible_responses)))

            max_proba_index = 0
            max_proba = 0

            for b, x in enumerate(predictions):
                if x[1] > max_proba:
                    max_proba_index = b
                    max_proba = x[1]


            print('Index: ', max_proba_index+1)
            print('Proba: ', str(max_proba*100)[0:5], '%')
            print('Reponse: ',  possible_responses[max_proba_index], '\n')
            for i in zip(range(1,16), predictions):
                print(i[0], ' - ', str(i[1][1]*100)[0:5], '%')

            chatResponse = possible_responses[max_proba_index]

            replyText = '.@' + screenName + ' [' + tweetText[bot_username_length+1:] + '] '+ chatResponse[len(start_text_seed):]

            #check if response is over 140 char
            if len(replyText) > 140:
                replyText = replyText[0:139] + '…'

            
            print('Reply Tweet: ' + replyText)

            # If rate limited, the status posts should be queued up and sent on an interval
            twitterApi.update_status(status=replyText, in_reply_to_status_id=tweetId)

    def on_error(self, status):
        print (status)

        # if rate limited, disconnect the stream
        if status == 420:
            return False


if __name__ == '__main__':
    streamListener = ReplyToTweet()
    twitterStream = Stream(auth, streamListener)
    twitterStream.userstream(_with='user')
