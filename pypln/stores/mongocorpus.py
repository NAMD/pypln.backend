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
from nltk.util import AbstractLazySequence, LazyMap, LazyConcatenation


class MongoDBLazySequence(AbstractLazySequence):
    def __init__(self, host='127.0.0.1', port=27017, db='test',
                 collection='documents', field='text'):
        self.conn = pymongo.Connection(host, port)
        self.collection = self.conn[db][collection]
        self.field = field

    def __len__(self):
        return self.collection.count()

    def iterate_from(self, start):
        f = lambda d: d.get(self.field, '')
        return iter(LazyMap(f, self.collection.find(fields=[self.field],
                                                    skip=start)))

class MongoDBCorpusReader(object):
    """ Corpus Reader to deal with text stored on a MongoDB collection """
    #TODO: introduce language specification to select appropriate tokenizers
    def __init__(self, word_tokenizer=None, sent_tokenizer=None, **kwargs):
        if word_tokenizer is None:
            word_tokenizer = TreebankWordTokenizer()
        if sent_tokenizer is None:
            sent_tokenizer = LazyLoader('tokenizers/punkt/english.pickle')
        self._seq = MongoDBLazySequence(**kwargs)
        self._word_tokenize = word_tokenizer.tokenize
        self._sent_tokenize = sent_tokenizer.tokenize

    def text(self):
        """ Return lazy iterator over the texts in the corpus.  """
        return self._seq

    #TODO: create decorators to cache token and sentence lists on the database
    def words(self):
        return LazyConcatenation(LazyMap(self._word_tokenize,self.text()))

    #TODO: change to 'sentences'?
    def sents(self):
        return LazyConcatenation(LazyMap(self._sent_tokenize,self.text()))
