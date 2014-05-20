# -*- coding: utf-8 -*-
import os.path
import subprocess
import sys

import config


def do_capture(tweet_id):
    outfile = os.path.join(config.local_folder, "screenshots")
    tmpfile = os.path.join(outfile, tweet_id + ".png")
    outfile = os.path.join(outfile, tweet_id + "_.png")

    if not os.path.isfile(outfile):
        cmd = 'xvfb-run --server-args="-screen 0, 1024x768x24" '
        cmd += ' cutycapt --url=https://twitter.com/uterope/status/'
        cmd += tweet_id
        cmd += ' --header=Accept-Language:en-US --min-width=650 '
        cmd += ' --out=' + tmpfile
        try:
            p = subprocess.check_call(cmd, shell=True)
        except subprocess.CalledProcessError as e:
            print "Error subprocess "
            print e

        cmd = "convert " + tmpfile + " -precision 8 -type palette "
        cmd += "-colors 100 " + outfile
        try:
            p = subprocess.check_call(cmd, shell=True)
        except subprocess.CalledProcessError as e:
            print "Error subprocess "
            print e

        try:
            os.remove(tmpfile)
        except:
            print "Error couldn't remove tmpfile"

def main():
    #tweet_id = 467337666879827968
    tweet_id = sys.argv[1].strip()
    do_capture(tweet_id)


if __name__ == "__main__":
    main()
