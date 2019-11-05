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

#daemon core
core = "/home/RonTipsProject/ronpaulcoind"
# core = "/home/akra/Documents/ronpaulcoind"

CONSUMER_KEY = 'WwcjStPWdebXlAd48KlULR4qm'
CONSUMER_SECRET = 'QPbtxFIrkUMNCRIfR7dlt5NZvkjZ0s4qCsHVGcnCWANbhdnlaJ'
ACCESS_KEY = '1100749378426261504-vWdlm7C5M42gaHhGEQLdWcGcvosrTL'
ACCESS_SECRET = 'MJnm9IidFpOcVfBcnZ7mPzjpBKoadrZrlkccFO3mwghbC'

# do twitter auth stuff
api = TwitterAPI(CONSUMER_KEY, 
    CONSUMER_SECRET,
    ACCESS_KEY,
    ACCESS_SECRET)

def run_bot(dm_replied_to):
    with open(dm_replied_to_file, "a") as logfile:
        dms = api.request('direct_messages/events/list').json()
        try:
            for dm in dms['events']:
                message = dm['message_create']['message_data']['text']
                sender_id = dm['message_create']['sender_id']
                recipient_id = dm['message_create']['target']['recipient_id']
                message_id = dm['id']
                print 'message_id: ' + message_id
                print 'message: ' + message
                print 'sender_id:'+ sender_id
                print 'recipient_id:'+recipient_id
                if message_id not in dm_replied_to:
                    try:
                        print 'new messsage'
                        print 'sender_id:' + sender_id
                        print 'recipient_id:' + recipient_id
                        dm_replied_to.append(message_id)
                        with open (dm_replied_to_file, "a") as f:
                            f.write(message_id + "\n")
                        if recipient_id == user_id:
                            print 'message from other'
                            dm_handler(sender_id, recipient_id, message, logfile)
                    except:
                        logfile.write('to frequent\n')
        except:
            print 'error'
        time.sleep(120)

def dm_handler(sender_id, recipient_id, message, logfile):
    print 'sending direct messages...'
    accountStr = "twitter-{0}".format(sender_id.lower())
    print "wallet accountname: {0}".format(accountStr)
    print "message lowered:" + message.lower()
    if 'balance' in message.lower():
        print 'inside the balance'
        if len(message.split())==1:
            # get balance data by running daemon ronpaulcoind
            balance = subprocess.check_output([core,"getbalance", accountStr])[:-1]
            send_dm(sender_id, 'Your balance is {0} RPC'.format(balance))
            print 'balance:'+balance
        else:
            send_dm(sender_id, 'Usage in PM: `balance`')
            print 'Balance error'
    elif 'deposit' in message.lower():
        print 'inside the deposit'
        print len(message.split())
        if len(message.split())==1:
            print 'inside getaccountaddress deposit'
            deposit = subprocess.check_output([core,"getaccountaddress", accountStr])[:-1]
            print deposit
            print 'Deposit\nYour depositing Your depositing address is: {0}'.format(deposit)
            send_dm(sender_id, "Your Ron Paul Coin depositing address is: {0}".format(deposit))
        else:
            send_dm(sender_id, "Usage in PM: `deposit`")
            print 'Deposit error\nUsage in PM: `deposit`'
    elif 'withdraw' in message.lower():
        print 'inside the withdraw'
        if len(message.split())==3:
            try:
                amount = float(message.split()[1])
                address = message.split()[2]
                # accountStr = 'reddit-{0}'.format(item.author.name)
                balance = float(subprocess.check_output([core,"getbalance", accountStr])[:-1])
                if balance < amount:
                    send_dm(sender_id, "You have insufficent funds.")
                    print 'Withdraw error\nYou have insufficent funds.'
                else:
                    amount = str(amount)
                    # sendfrom <fromaccount> <toronpaulcoinaddress> <amount> [minconf=1] [comment] [comment-to]
                    tx = subprocess.check_output([core,"sendfrom",accountStr,address,amount])[:-1]
                    # {0} has successfully withdrew to address: {1} of {2} RDD"
                    send_dm(sender_id, "You have successfully withdrawn {0} RPC to address: {1}".format(amount,address))
                    print 'Withdraw success\nYou have successfully withdrew to address: {0} of {1} RPC'.format(address,amount)
            except ValueError:
                send_dm(sender_id, "To withdraw your Ron Paul Coin please PM the following: withdraw <amount> <address>")
                print 'Withdraw error\nUsage in PM: `withdraw <amount> <address>`'
        else:
            send_dm(sender_id, "To withdraw your Ron Paul Coin please PM the following: withdraw <amount> <address>")
            print 'Withdraw error\nUsage in PM: `withdraw <amount> <address>`'

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

def get_saved_dms():
    if not os.path.isfile(dm_replied_to_file):
        dm_replied_to = []
    else:
        with open(dm_replied_to_file, "r") as f:
            dm_replied_to = f.read()
            dm_replied_to = dm_replied_to.split("\n")
            dm_replied_to = filter(None, dm_replied_to)
    return dm_replied_to

dm_replied_to = get_saved_dms()

while True:
    run_bot(dm_replied_to)
    pass