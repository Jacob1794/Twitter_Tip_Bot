#!/usr/bin/env python
from TwitterAPI import TwitterAPI
import json
import subprocess
import time
import os
import config

dmLogFile = 'dmLog.txt'
dm_replied_to_file = 'dm_replied_to.txt'
user_id = '1100749378426261504'

# tweet['user']['id'] //TrustyMan77
# tweet['in_reply_to_user_id'] // TipBot id

#daemon core
core = "/home/RonTipsProject/ronpaulcoind"

CONSUMER_KEY = 'WwcjStPWdebXlAd48KlULR4qm'
CONSUMER_SECRET = 'QPbtxFIrkUMNCRIfR7dlt5NZvkjZ0s4qCsHVGcnCWANbhdnlaJ'
ACCESS_KEY = '1100749378426261504-vWdlm7C5M42gaHhGEQLdWcGcvosrTL'
ACCESS_SECRET = 'MJnm9IidFpOcVfBcnZ7mPzjpBKoadrZrlkccFO3mwghbC'

# last_seen_id
FILE_NAME = 'last_seen_id.txt'
# do twitter auth stuff
api = TwitterAPI(CONSUMER_KEY, 
    CONSUMER_SECRET,
    ACCESS_KEY,
    ACCESS_SECRET)

def get_tweets(last_seen_id):
    tweets = api.request('statuses/mentions_timeline',{ 'since_id':last_seen_id }).json()
    return tweets

def send_notification(message, tweet_id):
    reply_message = api.request('statuses/update',{'status':message, 'in_reply_to_status_id':tweet_id})
    if reply_message['errors']:
        return 'error'
    else:
        return 'success'

def send_dm(recipient_id, message):
    event = {
        "event": {
            "type": "message_create",
            "message_create": {
                "target": {
                    "recipient_id": recipient_id
                },
                "message_data": {
                    "text": message
                }
            }
        }
    }
    r = api.request('direct_messages/events/new', json.dumps(event))
    print('SUCCESS' if r.status_code == 200 else 'PROBLEM: ' + r.text)

def get_user_id_from_name(user_name):
    try:
        user_id = api.request('users/show',{'screen_name':user_name}).json()['id']
        return user_id
    except:
        return 'error'

def get_user_name_from_id(user_id):
    try:
        screen_name = api.request('users/show',{'user_id':user_id}).json()['screen_name']
        return screen_name
    except:
        return 'error'

def retrieve_last_seen_id(file_name):
    f_read = open(file_name, 'r')
    last_seen_id = int(f_read.read().strip())
    f_read.close()
    return last_seen_id

def store_last_seen_id(last_seen_id, file_name):
    f_write = open(file_name, 'w')
    f_write.write(str(last_seen_id))
    f_write.close()
    return

def tip(sender_id, sender_name, tweet_id, message):
    print 'it is inside tip function\n'
    # sender = comment.author.name.lower()
    if len(message.split()) == 4:
        amount = message.split()[2]
        try:
            amount = float(amount)
            recipient = message.split()[3]
            if recipient[0]=='@':
                try:
                    recipient = recipient[1:]
                    print "recipient:"
                    print recipient
                    recipient_id = get_user_id_from_name(recipient)
                    if recipient_id != 'error': # if it is valid user
                        print 'no error'
                        print recipient_id
                        senderStr = 'twitter-{0}'.format(sender_id)
                        receiverStr = 'twitter-{0}'.format(recipient_id)
                        result = subprocess.check_output([core,"getbalance", senderStr])[:-1]
                        print 'error here'
                        balance = float(result)
                        print"balance:\n{0}".format(balance)
                        print "---------------\n"
                        print "receiver:\n{0}".format(receiverStr)
                        print "sender:\n{0}".format(senderStr)
                        if balance < amount:
                            # send_dm(sender_id, "{0}, you have insufficent funds.".format(sender_name))
                            send_notification("@{0}, you have insufficent funds.".format(sender_name), tweet_id)
                            print "{0}, you have insufficent funds.".format(sender_name)
                        elif recipient == sender_name:
                            # comment.reply("You can't tip yourself silly.")
                            # send_dm(sender_id, "You can't tip yourself silly.")
                            send_notification("@{0}, you can't tip yourself silly.".format(sender_name), tweet_id)
                            print "You can't tip yourself silly."
                        else:
                            balance = str(balance)
                            amount = str(amount)
                            # check if the receiver has wallet account
                            addresses = subprocess.check_output([core, "getaddressesbyaccount", receiverStr])
                            if len(addresses.split())==2:
                                subprocess.check_output([core,"getaccountaddress", receiverStr])
                            # send coin to custom reddit user
                            tx = subprocess.check_output([core,"move",senderStr,receiverStr,amount])[:-1]
                            # comment.reply("@{0} tipped @{1}RPC to @{2}".format(sender, amount, receiver))
                            # reddit.redditor(sender).message('Tip', "@{0} tipped @{1}RPC to @{2}".format(sender, amount, receiver))
                            # send_dm(recipient_id, "{0} tipped you {1} of Ron Paul Coin via the RonTips4Liberty tipping bot. For  instructions on how to withdraw, tip other users & more, visit https://www.reddit.com/r/RonTips4Liberty/wiki/index".format(sender_name, amount))
                            send_notification("@{0}, {1} tipped you {2} of Ron Paul Coin via the RonTips4Liberty tipping bot. For  instructions on how to withdraw, tip other users & more, visit https://www.reddit.com/r/RonTips4Liberty/wiki/index".format(recipient, sender_name, amount), tweet_id)
                            print "{0} tipped {1}RPC to you".format(sender_name, amount)
                    else:
                        # send_dm(sender_id, "Invalid user error!")
                        send_notification("@{0}, invalid user error!".format(sender_name), tweet_id)
                        print "Invalid user error!"
                except Exception as ex:
                    template = "An exception of type {0} occurred. Arguments:\n{1!r}"
                    message = template.format(type(ex).__name__, ex.args)
                    print message
            else:
                # send_dm(sender_id, "Usage in comment: `tip <amount> @<username>`")
                send_notification("Usage in comment: `tip <amount> @<username>`", tweet_id)
                print 'Tip error: {0}'.format(message)
        except ValueError:
            # send_dm(sender_id, "Usage in comment: `tip <amount> @<username>`")
            send_notification("Usage in comment: `tip <amount> @<username>`", tweet_id)
            print 'Tip amount error: {0}'.format(message)
    else:
        # send_dm(sender_id, "Usage in comment: `tip <amount> @<username>`")
        send_notification("Usage in comment: `tip <amount> @<username>`", tweet_id)
        print 'Tip format error: {0}'.format(message)

def reply_to_tweets(api):
    print 'retrieving and replying to tweets...'
    last_seen_id = retrieve_last_seen_id(FILE_NAME)
    try:
        print last_seen_id
        mentions = get_tweets(last_seen_id)
        for mention in reversed(mentions):
            print last_seen_id
            last_seen_id = mention['id'] # save last seen tweet id
            store_last_seen_id(last_seen_id, FILE_NAME) # save last seen id to file
            message = mention['text'].lower()
            sender_id = mention['user']['id'] # tip sender id
            sender_name = mention['user']['screen_name']
            if 'tip' == message.split()[1]:
                tip(sender_id, sender_name, last_seen_id, message)
            # if '#helloworld' in mention.text.lower():
            #     print 'found #helloworld'
            # api.update_status('@' + mention.user.screen_name + '#helloworld back to you!', mention.id) # tweet reply
    except Exception as ex:
        print ex
    print 'sleeping 10 seconds'
    time.sleep(10)

while True:
    reply_to_tweets(api)
    pass