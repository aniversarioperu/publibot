# -*- coding: utf-8 -*-
import codecs
from datetime import datetime
import json
import os
import os.path
import re
import shutil
import subprocess
from time import sleep

import dataset
import requests
import sqlalchemy

import api
import config
from bot import get_user_list
from take_screenshot import do_capture


def generate_site():
    report_cherry()
    shutil.copy2(
            os.path.join(config.local_folder, "cherry_tweets.json"),
            os.path.join(config.dest_folder, "cherry_tweets.json")
    )
    shutil.copy2(
            os.path.join(config.local_folder, "index.html"),
            os.path.join(config.dest_folder, "index.html")
    )
    shutil.copy2(
            os.path.join(config.local_folder, "js/get_tweets.js"),
            os.path.join(config.dest_folder, "js/get_tweets.js")
    )
    shutil.copy2(
            os.path.join(config.local_folder, "css/style.css"),
            os.path.join(config.dest_folder, "css/style.css")
    )
    shutil.copy2(
            os.path.join(config.local_folder, "config.py"),
            os.path.join(config.dest_folder, "config.py")
    )
    cmd = "rsync -au " + os.path.join(config.local_folder, "screenshots/*")
    cmd += " " + config.dest_folder + "/screenshots/."
    p = subprocess.check_call(cmd, shell=True)


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
            tuit = json.loads(line.strip())
            tuit['screen_name'] = tuit['screen_name'].lower()
            tuits.append(tuit)
    table.insert_many(tuits)


def get_since_id(twitter_handle, db):
    # get the last tweet for that user in our database
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

    # do connection here
    dbfile = os.path.join(config.local_folder, "tuits.db")
    db = dataset.connect("sqlite:///" + dbfile)

    for user in get_user_list():
        twitter_handle = user[1].replace("@", "").lower()
        print twitter_handle
        #twitter_handle = "munimiraflores"
        since_id = get_since_id(twitter_handle, db)
        get_tuits_since(since_id, twitter_handle, db)


def upload_my_tweet(tweet, db):
    table = db['tuits']
    if table.find_one(tweet_id=tweet['tweet_id']) is None:
        res = table.insert(tweet)
        #print res
        print "\nUploaded @" + tweet['screen_name'] 
        print tweet['status'].encode("utf8")

        # take screenshot of tweet
        do_capture(str(tweet['tweet_id']))


def get_tuits_since(since_id, twitter_handle, db):
    oauth = api.get_oauth()

    url = "https://api.twitter.com/1.1/statuses/user_timeline.json"
    payload = {
        'screen_name': twitter_handle,
        'count': 200,
        'since_id': since_id,
    }
    print payload
    try:
        sleep(6)
        r = requests.get(url, auth=oauth, params=payload)
        data = r.json()
        for item in data:
            if 'id' in item:
                tweet = {}
                tweet['tweet_id'] = item['id']
                tweet['screen_name'] = item['user']['screen_name'].lower()
                tweet['user_id'] = item['user']['id']
                tweet['status'] = item['text']
                tweet['created_at'] = item['created_at']
                tweet['utc_offset'] = item['user']['utc_offset']
                if 'geo' in item and item['geo']:
                    tweet['latitude'] = item['geo']['coordinates'][0]
                    tweet['longitude'] = item['geo']['coordinates'][1]
                #print tweet
                upload_my_tweet(tweet, db)
            else:
                print "Didnt get tuits", data
    except requests.exceptions.ConnectionError as e:
        print("Error", e)


def get_screenshots_using_db():
    # publicidad está prohibida desde esta fecha
    DATE_LIMIT = datetime(2014, 1, 24, 0, 0)

    dbfile = os.path.join(config.local_folder, "tuits.db")
    db = dataset.connect("sqlite:///" + dbfile)
    res = db.query("select * from tuits")
    for i in res:
        print "Created at %s" % i['created_at']
        date = datetime.strptime(i['created_at'], "%a %b %d %H:%M:%S +%f %Y")
        if date > DATE_LIMIT:
            screenshot_filename = "screenshots/" + str(i['tweet_id']) + ".png"
            #if not os.path.isfile(screenshot_filename):
                #cmd = "python take_screenshot.py " + str(i['tweet_id'])
                #p = subprocess.check_call(cmd, shell=True)


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


def extract_all_status():
    # publicidad está prohibida desde esta fecha
    DATE_LIMIT = datetime(2014, 1, 24, 0, 0)

    dbfile = os.path.join(config.local_folder, "tuits.db")
    db = dataset.connect("sqlite:///" + dbfile)
    res = db.query("select * from tuits")

    f = codecs.open("all_status.txt", "w", "utf-8")
    for i in res:
        date = datetime.strptime(i['created_at'], "%a %b %d %H:%M:%S +%f %Y")
        if date < DATE_LIMIT:
            status = i['status'].replace("\n", " ")
            output = status + "\t|||\t" + str(i['tweet_id']) + "\n"
            f.write(output)
    f.close()


def process_tuit_msg(tuit):
    tuit = re.sub("(https*://\w+\.\w+\/\w+)","<a href='\\1'>\\1</a>", tuit)

    pattern = "@([a-zA-Z0-9_]{1,15})"
    tuit = re.sub(pattern ,"<a href='https://twitter.com/\\1'>@\\1</a>", tuit)

    pattern = "#(\w+)"
    mystring = "<a href='https://twitter.com/search?q=%23\\1'>#\\1</a>"
    tuit = re.sub(pattern, mystring, tuit)
    return tuit


def retweet(i):
    oauth = api.get_oauth()

    status = "#publicidadRestringida? RT @" + i['screen_name']
    status += " " + i['orig_status'][0:80]
    status += " " + "https://twitter.com/" + i['screen_name']
    status += "/status/" + str(i['tweet_id'])

    url = "https://api.twitter.com/1.1/statuses/update.json"
    payload = {
        'status': status,
    }
    print payload
    try:
        sleep(6)
        r = requests.post(url, auth=oauth, params=payload)
        print r.json()
    except requests.exceptions.ConnectionError as e:
        print("Error", e)


def report_cherry():
    # cherry tweets with forbidden adverts
    # input a list of keywords
    keywords = os.path.join(config.local_folder, "keywords.txt")

    # make query
    query = "select screen_name, tweet_id, created_at, status from tuits where "
    for line in codecs.open(keywords, "r", "utf8").readlines():
        line = line.strip()
        query += "status like '%" + line + "%' OR "
    query = re.sub(" OR $", "", query)
    query += " order by tweet_id desc"

    # publicidad está prohibida desde esta fecha
    DATE_LIMIT = datetime(2014, 1, 24, 0, 0)

    dbfile = os.path.join(config.local_folder, "tuits.db")
    db = dataset.connect("sqlite:///" + dbfile)
    table = db['tuits']
    res = db.query(query)

    cherry_tweets = []
    for i in res:
        date = datetime.strptime(i['created_at'], "%a %b %d %H:%M:%S +%f %Y")
        if date > DATE_LIMIT:
            i['created_at'] = date.strftime('%b %d, %Y')
            i['tweet_id'] = str(i['tweet_id'])
            i['orig_status'] = i['status']
            i['status'] = process_tuit_msg(i['status'])
            cherry_tweets.append(i)
    f = codecs.open("cherry_tweets.json", "w", "utf-8")
    for i in cherry_tweets:
        f.write(json.dumps(i) + "\n")
        i['tweet_id'] = int(i['tweet_id'])
        table.update(i, ['tweet_id'])
    f.close()


def get_profile_image_url():
    user_list = get_user_list()
    oauth = api.get_oauth()
    for user in user_list:
        url = "https://api.twitter.com/1.1/users/show.json"
        screen_name = user[1].replace("@", "")
        payload = {
            'screen_name': screen_name,
        }
        r = requests.get(url, auth=oauth, params=payload)
        profile_url = r.json()['profile_image_url']
        download_profile_image(profile_url, screen_name)


def download_profile_image(url, screen_name):
    # folder to keep our twitter profile images
    directory = os.path.join(config.local_folder, "avatars")

    if not os.path.exists(directory):
        os.makedirs(directory)

    path = screen_name + ".jpg"
    path = os.path.join(directory, path.lower())
    if not os.path.isfile(path):
        r = requests.get(url, stream=True)
        if r.status_code == 200:
            with open(path, 'wb') as f:
                for chunk in r.iter_content():
                    f.write(chunk)

    return screen_name.lower()


#upload_starting_data()
def main():
    update_our_database()


if __name__ == "__main__":
    main()
