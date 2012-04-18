#!/usr/bin/env python
#-*- coding:utf-8 -*-
"""
This script offer the ability to import wordlist from unix dict files to a mongodb collection
"""

__author__ = 'fccoelho'
__docformat__ = "restructuredtext en"

import argparse
from glob import glob
import os
import subprocess
from mongoengine import *
import codecs
import chardet

connect('Dictionaries')

class Wordlist(Document):
    dictionary = StringField(required=True)
    words = ListField(StringField())

# If we had words with their associated meanings, we could create a collection of  words and embed them in wordlist with:  ListField(EmbeddedDocumentField(Comment))

def get_dict_list():
    """

    :return: Lists of available wordlist in the system
    """
    dict_list = []
    for l in glob("/usr/share/dict/*"):
        if os.path.islink(l):
            continue
        f = os.path.split(l)[-1]
        if f.startswith('README'):
            continue
        dict_list.append(l)
    return dict_list

def start_import(listofdicts=[]):
    """
    Load list of dicts on mongo
    :param listofdicts: List of dicts to import
    :return:
    """
    for di in get_dict_list():
        if not listofdicts or di in listofdicts:
            add_to_mongo(di)

def add_to_mongo(fname):
    """

    :param file:
    :return:
    """
    p = subprocess.Popen(['file',fname],stdout=subprocess.PIPE) # Find the encoding
    encoding,stderr = p.communicate()
    encoding = {'Unicode':'utf8','ISO-8859':'iso8859'}[encoding.split()[-2]]
    print "processing %s"%fname
    print "encoding: ",encoding
    with codecs.open(fname,'r',encoding=encoding) as f:
        try:
            wordlist = f.read().split()
        except UnicodeDecodeError as e:
            print e
#            print "Unicode error while processing %s because of character %s: "%(fname,unichr(e.__repr__().split('in')[0].split()[-1])) ,e
            return
    wld = Wordlist()
    wld.dictionary=fname
    wld.words=wordlist
#    print wordlist
    wld.save()

    pass


if __name__=="__main__":
#    parser = argparse.ArgumentParser(description='Scans /usr/share/dict/ for dict files to import')
#    #group = parser.add_mutually_exclusive_group(required=True)
#    parser.add_argument('-l', '--list', action=get_dict_list, help='list available wordlists')
#
#
#    args = parser.parse_args()
    start_import()