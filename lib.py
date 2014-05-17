# -*- coding: utf-8 -*-
import codecs
from datetime import datetime
import glob
import json
import os
import os.path
import subprocess
from time import sleep

import dataset
import requests

import api
import config
from bot import get_user_list


def create_database():
    dbfile = os.path.join(config.local_folder, "tuits.db")
    if not os.path.isfile(dbfile):
        try:
            print "Creating database"
            db = dataset.connect('sqlite:///' + dbfile)
            table = db.create_table("tuits")
            table.create_column('tweet_id', sqlalchemy.BigInteger)
            table.create_column('screen_name', sqlalchemy.Text)
            table.create_column('user_id', sqlalchemy.BigInteger)
            table.create_column('status', sqlalchemy.Text)
            table.create_column('created_at', sqlalchemy.String)
            table.create_column('utc_offset', sqlalchemy.Integer)
            table.create_column('latitude', sqlalchemy.Float(precision=7))
            table.create_column('longitude', sqlalchemy.Float(precision=7))
        except:
            pass


def upload_starting_data():
    create_database()

    dbfile = os.path.join(config.local_folder, "tuits.db")
    db = dataset.connect("sqlite:///" + dbfile)
    table = db['tuits']

    filename = "tuits.json"
    tuits = []
    with codecs.open(filename, "r", "utf-8") as handle:
        for line in handle.readlines():
            tuit = json.loads(line)
            tuit['screen_name'] = tuit['screen_name'].lower()
            tuits.append(tuit)
    table.insert_many(tuits)


def get_since_id(twitter_handle):
    # get the last tweet for that user in our database
    dbfile = os.path.join(config.local_folder, "tuits.db")
    db = dataset.connect("sqlite:///" + dbfile)
    query = "select tweet_id from tuits where "
    query += "screen_name='" + twitter_handle + "' "
    query += "order by tweet_id desc limit 1"
    res = db.query(query)
    for i in res:
        since_id = i['tweet_id']
        print "Found since_id # %i" % since_id
        return since_id


def update_our_database():
    create_database()

    for user in get_user_list():
        twitter_handle = user[1].replace("@", "").lower()
        print twitter_handle
        #twitter_handle = "munimiraflores"
        since_id = get_since_id(twitter_handle)
        get_tuits_since(since_id, twitter_handle)


def upload_my_tweet(tweet):
    dbfile = os.path.join(config.local_folder, "tuits.db")
    db = dataset.connect("sqlite:///" + dbfile)
    table = db['tuits']
    if table.find_one(tweet_id=tweet['tweet_id']) is None:
        table.insert(tweet)
        print "Uploaded @%s: %s\n" % (tweet['screen_name'], tweet['status'])

        # take screenshot of tweet
        cmd = "python take_screenshot.py " + str(tweet['tweet_id'])
        p = subprocess.check_call(cmd, shell=True)


def get_tuits_since(since_id, twitter_handle):
    oauth = api.get_oauth()

    url = "https://api.twitter.com/1.1/statuses/user_timeline.json"
    payload = {
        'screen_name': twitter_handle,
        'count': 200,
        'since_id': since_id,
        }
    print payload
    try:
        sleep(4)
        r = requests.get(url, auth=oauth, params=payload)
        data = r.json()
        for item in data:
            tweet = {}
            tweet['tweet_id'] = item['id']
            tweet['screen_name'] = item['user']['screen_name'].lower()
            tweet['user_id'] = item['user']['id']
            tweet['status'] = item['text']
            tweet['created_at'] = item['created_at']
            tweet['utc_offset'] = item['user']['utc_offset']
            if 'geo' in item and item['geo'] != None:
                tweet['latitude'] = item['geo']['coordinates'][0]
                tweet['longitude'] = item['geo']['coordinates'][1]
            print tweet
            upload_my_tweet(tweet)
    except requests.exceptions.ConnectionError:
        print("Error", r.text)


def get_screenshots_using_db():
    # publicidad está prohibida desde esta fecha
    DATE_LIMIT = datetime.datetime(2014, 1, 24, 0, 0)

    dbfile = os.path.join(config.local_folder, "tuits.db")
    db = dataset.connect("sqlite:///" + dbfile)
    res = db.query("select * from tuits")
    for i in res:
        date = datetime.strptime(i['created_at'], "%a %b %d %H:%M:%S +%f %Y")
        if date > DATE_LIMIT:
            screenshot_filename = "screenshots/" + str(i['tweet_id']) + ".png"
            if not os.path.isfile(screenshot_filename):
                cmd = "python take_screenshots.py " + str(i['tweet_id'])
                p = subprocess.check_call(cmd, shell=True)


def delete_unnecessary_screenshots_using_db():
    # publicidad está prohibida desde esta fecha
    DATE_LIMIT = datetime(2014, 1, 24, 0, 0)

    dbfile = os.path.join(config.local_folder, "tuits.db")
    db = dataset.connect("sqlite:///" + dbfile)
    res = db.query("select * from tuits")
    for i in res:
        date = datetime.strptime(i['created_at'], "%a %b %d %H:%M:%S +%f %Y")
        if date < DATE_LIMIT:
            screenshot_filename = "screenshots/" + str(i['tweet_id']) + ".png"
            if os.path.isfile(screenshot_filename):
                os.remove(screenshot_filename)
                print "Removed file %s" % screenshot_filename


#upload_starting_data()
def main():
    update_our_database()


if __name__ == "__main__":
    main()
