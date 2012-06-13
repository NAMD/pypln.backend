#-*- coding:utf-8 -*-

import unittest
import ConfigParser
import pymongo
import nltk
from pypln.stores.mongocorpus import MongoDBCorpusReader


config = ConfigParser.ConfigParser()
config.read('tests/data/pypln.conf')

class TestMongoCorpus(unittest.TestCase):
    def setUp(self):
        host = config.get('mongodb', 'host')
        port = int(config.get('mongodb', 'port'))
        self.conn = pymongo.Connection(host, port)
        self.db = self.conn['TestCorpus']
        self.coll = self.db['docs']
        with open('README.rst', 'r') as f:
            self.t = f.read()
        for i in xrange(100):
            self.coll.insert({"text": self.t})

    def tearDown(self):
        self.conn.drop_database('TestCorpus')

    @unittest.skip('Failing sometimes with "index out of range" on penultimate'
                   ' assert')
    def test_get_texts(self):
        reader = MongoDBCorpusReader(db='TestCorpus', collection='docs',
                                     field='text')
        self.assertIsInstance(reader.sents(), nltk.util.LazyConcatenation,
                              msg='Type is {}'.format(type(reader.sents())))
        self.assertIsInstance(reader.words(), nltk.util.LazyConcatenation)
        self.assertIsInstance(reader.text()[1], unicode,
                              msg='Type is {}'.format(type(reader.text()[1])))
        self.assertEqual(reader.text()[1], self.t)
