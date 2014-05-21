#!/usr/bin/python

import json
import cgi
import cgitb
import codecs
import re
import string
import sys

import dataset

import config


cgitb.enable()
data = cgi.FieldStorage()


def make_query(start):
    f = codecs.open("cherry_tweets.json", "r", "utf-8")
    lines = []
    start = int(start)
    end = int(start) + 20
    for i, line in enumerate(f):
        if i >= start and i < end:
            lines.append(json.loads(line))
    f.close()
    return lines


def sanitize(s):
    s = s.replace("'", "")
    s = s.replace('"', "")
    s = s.replace("/", "")
    s = s.replace("\\", "")
    s = s.replace(";", "")
    s = s.replace("=", "")
    s = s.replace("*", "")
    s = s.replace("%", "")
    return s

if 'start' in data:
    start = sanitize(data['start'].value)
    data = make_query(start)

    print "Content-Type: application/json\n"
    print json.dumps({"out": data})
else:
    pass
