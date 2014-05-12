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
        data = False
        twitter_handle = user[1].replace("@", "")
        payload = {
            'screen_name': twitter_handle,
            'count': 2,
            }
        try:
            r = requests.get(url, auth=oauth, params=payload)
            data = r.json()
            for i in data:
                tweet = {}
                tweet['tweet_id'] = i['id']
                tweet['screen_name'] = i['user']['screen_name']
                tweet['user_id'] = i['user']['id']
                tweet['status'] = i['text']
                f = open("tuits.csv", "w")
                f.write(json.dumps(tweet, indent=4))
                f.close()
                sys.exit(0)
        except requests.exceptions.ConnectionError:
            print("Error", r.text)


def main():
    # publicidad estatal prohibida desde el 24 de Enero

    # authorities list
    user_list = get_user_list()

    get_recent_tweets(user_list)



if __name__ == "__main__":
    main()
