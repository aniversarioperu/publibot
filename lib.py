import codecs
import glob
import json
import os
import os.path

import dataset

import config


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

def upload_staring_data():
    create_database()

    dbfile = os.path.join(config.local_folder, "tuits.db")
    db = dataset.connect("sqlite:///" + dbfile)
    table = db['tuits']

    filename = "tuits.json"
    with codecs.open(filename, "r", "utf-8") as handle:
        tuits = [json.loads(line) for line in handle.readlines()]
    table.insert_many(tuits)


upload_staring_data()

