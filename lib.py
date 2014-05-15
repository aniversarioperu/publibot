import codecs
import glob
import json
import os
import os.path

import dataset

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
    twitter_handle = "munimiraflores"
    # get the last tweet for that user in our database
    dbfile = os.path.join(config.local_folder, "tuits.db")
    db = dataset.connect("sqlite:///" + dbfile)
    query = "select * from tuits where screen_name='" + twitter_handle
    query += "'"
    print query
    res = db.query(query)
    for i in res:
        print i, twitter_handle


def update_our_database():
    create_database()

    url = "https://api.twitter.com/1.1/statuses/user_timeline.json"
    for user in get_user_list():
        twitter_handle = user[1].replace("@", "")
        print get_since_id(twitter_handle)




#upload_starting_data()
update_our_database()
