from keys import keys

import json
import subprocess
from time import sleep

from tweepy.streaming import StreamListener
from tweepy import OAuthHandler
from tweepy import Stream
from tweepy import API

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
        print('Tweet Received!  Preparing response...')
        tweet = json.loads(data.strip())
        
        retweeted = tweet.get('retweeted')
        from_self = tweet.get('user',{}).get('id_str','') == account_user_id

        if retweeted is not None and not retweeted and not from_self:

            tweetId = tweet.get('id_str')
            screenName = tweet.get('user',{}).get('screen_name')
            tweetText = tweet.get('text')

            
            bot_username_length = len(stream_rule)
            start_text_seed = tweetText[bot_username_length:]
            length = str(140 - len(start_text_seed))
            
            # 0.0 - 1.0, higher == more 'creative'
            temperature = str(0.6)

            bash = ['th', 'sample.lua', '-checkpoint', checkpoint_file_path, '-length', length, '-temperature', temperature, '-start_text', start_text_seed, '-gpu', '-1']

            process = subprocess.run(bash, cwd=torch_rnn_path, stdout=subprocess.PIPE)
            # wait for bash output to finish
            sleep(10)

            chatResponse = str(process.stdout.decode('utf-8'))[:-len(screenName)]

            replyText = '.@' + screenName + ' ' + chatResponse

            #check if response is over 140 char
            if len(replyText) > 140:
                replyText = replyText[0:139] + '…'

            print('Tweet ID: ' + tweetId)
            print('From: ' + screenName)
            print('Tweet Text: ' + tweetText)
            print('Reply Text: ' + replyText)

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
