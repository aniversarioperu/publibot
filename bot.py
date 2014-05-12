# -*- coding: utf-8 -*-
#!/usr/bin/env python

import argparse
from argparse import RawTextHelpFormatter
import codecs
import sys


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


def main():
    user_list = get_user_list()
    print user_list


if __name__ == "__main__":
    main()
