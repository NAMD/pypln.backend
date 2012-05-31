#-*- coding:utf-8 -*-
"""
This module implements a MongoDB backed NLTK Corpus reader.
Adapted from the book "Text processing with NLTK cookbook

Usage:
=====
Instantiate MongoDBCorpusReader with parameter for host, port, db, collection and field
"""
__author__ = 'flavio'

import pymongo
from nltk.data import LazyLoader
from nltk.tokenize import TreebankWordTokenizer
from nltk import FreqDist
from nltk.util import AbstractLazySequence, LazyMap, LazyConcatenation
from pypln.logger import make_log

log = make_log(__name__)

class MongoDBLazySequence(AbstractLazySequence):
    """
    """
    def __init__(self,host="127.0.0.1", port=27017, db='test',collection='Documentos',field='text'):
        self.conn = pymongo.Connection(host,port)
        self.collection = self.conn[db][collection]
        self.field = field

    def __len__(self):
        return self.collection.count()

    def iterate_from(self, start):
        f = lambda d: d.get(self.field,'')
        return iter(LazyMap(f,self.collection.find(fields=[self.field],skip=start)))

class MongoDBCorpusReader(object):
    """
    Corpus Reader to deal with text stored on a collection of a MongoDB database.
    """
    #TODO: introduce language specification to select appropriate tokenizers
    def __init__(self,word_tokenizer=TreebankWordTokenizer(),sent_tokenizer=LazyLoader('tokenizers/punkt/english.pickle'),**kwargs):
        self._seq = MongoDBLazySequence(**kwargs)
        self._word_tokenize = word_tokenizer.tokenize
        self._sent_tokenize = sent_tokenizer.tokenize
    def text(self):
        """
        Returns lazy iterator over the texts in the corpus.
        """
        return self._seq
#TODO: create decorators to cache token lists and sentence lists on the database
    def words(self):
        return LazyConcatenation(LazyMap(self._word_tokenize,self.text()))
    def sents(self):
        return LazyConcatenation(LazyMap(self._sent_tokenize,self.text()))

