# -*- coding: utf-8 -*-
#!/usr/bin/env python

import argparse
from argparse import RawTextHelpFormatter
import codecs
import json
import sys

import requests

import api


description = u'Monitorea tuiter en búsqueda de publidad estatal'
parser = argparse.ArgumentParser(
    description=description,
    formatter_class=RawTextHelpFormatter,
    )
parser.add_argument(
    '-p',
    '--page',
    action='store_true',
    help='Generate Google Map page',
    required=False,
    dest='page'
    )

args = parser.parse_args()


def get_user_list():
    with codecs.open("lista_autoridades.csv", "r", "utf-8") as handle:
        user_list = [line.strip().split(",") for line in handle if '@' in line]
    return user_list


def get_recent_tweets(user_list):
    oauth = api.get_oauth()

    url = "https://api.twitter.com/1.1/statuses/user_timeline.json"
    for user in user_list:
        max_id = 0
        new_max_id = None
        data = False
        twitter_handle = user[1].replace("@", "")
        filename = twitter_handle + ".json"

        i = 0
        while max_id != new_max_id:
            print "Max_id" , max_id
            print "New_max_id" , new_max_id

            if max_id == 0 or max_id == None:
                payload = {
                    'screen_name': twitter_handle,
                    'count': 200,
                    }
            else:
                new_max_id = get_max_id(filename)
                max_id = new_max_id
                payload = {
                    'screen_name': twitter_handle,
                    'count': 200,
                    'max_id': max_id,
                    }

            try:
                print payload
                r = requests.get(url, auth=oauth, params=payload)
                data = r.json()
                for item in data:
                    tweet = {}
                    tweet['tweet_id'] = item['id']
                    tweet['screen_name'] = item['user']['screen_name']
                    tweet['user_id'] = item['user']['id']
                    tweet['status'] = item['text']
                    f = codecs.open(filename, "a+", "utf-8")
                    f.write(json.dumps(tweet) + "\n")
                    f.close()
                    max_id = get_max_id(filename)
            except requests.exceptions.ConnectionError:
                print("Error", r.text)


def get_max_id(filename):
    try:
        with codecs.open(filename, "r", "utf-8") as handle:
            ids = [json.loads(i)['tweet_id'] for i in handle]
        # return smallest number
        return sorted(ids)[0]
    except:
        return None


def main():
    # publicidad estatal prohibida desde el 24 de Enero

    # authorities list
    user_list = get_user_list()

    get_recent_tweets(user_list)



if __name__ == "__main__":
    main()
