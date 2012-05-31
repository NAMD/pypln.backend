#-*- coding:utf-8 -*-
"""
Created on 30/05/12
by fccoelho
license: GPL V3 or Later
"""

__docformat__ = 'restructuredtext en'

import unittest
from pypln.stores import filestor
from pypln.stores.mongocorpus import MongoDBCorpusReader
import gridfs
import nltk
import pymongo
import ConfigParser

config = ConfigParser.ConfigParser()
config.read('tests/pypln.test.conf')

class TestFileStore(unittest.TestCase):
    def test_create_connect(self):
        fs = filestor.FS("test",usr='usu',pw='pass',create=True)
        self.assertIsInstance(fs.fs,gridfs.GridFS)
        fs.drop()

class TestMongoCorpus(unittest.TestCase):
    def setUp(self):
        host = config.get('mongodb','host')
        port = int(config.get('mongodb','port'))
        self.conn = pymongo.Connection(host,port)
        self.db = self.conn['TestCorpus']
        self.coll = self.db['docs']
        with open('README.rst','r') as f:
            self.t = f.read()
        [self.coll.insert({"text":self.t}) for i in xrange(100)]
    def tearDown(self):
        self.conn.drop_database('TestCorpus')
    def test_get_texts(self):
        reader = MongoDBCorpusReader(db='TestCorpus', collection='docs',field='text')
        self.assertIsInstance(reader.sents(),nltk.util.LazyConcatenation,msg="type is %s"%type(reader.sents()))
        self.assertIsInstance(reader.words(), nltk.util.LazyConcatenation)
        self.assertIsInstance(reader.text()[1],unicode, msg="Type is %s"%type(reader.text()[1]))
        self.assertEqual(reader.text()[1],self.t)


