# coding: utf-8

import unittest
import datetime
import pymongo
from gridfs import GridFS
from pypln.stores.mongo import MongoDBStore
from bson import ObjectId


class TestMongoStore(unittest.TestCase):
    def setUp(self):
        config = {'db': {'host': 'localhost', 'port': 27017,
                         'database': 'pypln',
                         'corpora_collection': 'corpora',
                         'document_collection': 'documents',
                         'gridfs_collection': 'files',
                         'monitoring_collection': 'monitoring'},
                  'monitoring interval': 60,}
        #TODO: unify config
        self.db_conf = db_conf = config['db']
        self.connection = pymongo.Connection(host=db_conf['host'],
                                             port=db_conf['port'])
        self.db = self.connection[db_conf['database']]
        self.documents = self.db[db_conf['document_collection']]
        self.gridfs = GridFS(self.db, db_conf['gridfs_collection'])
        self.corpora = self.db[self.db_conf['corpora_collection']]
        self.store = MongoDBStore(**db_conf)
        self.documents.drop()
        self.corpora.drop()
        self.db[db_conf['gridfs_collection'] + '.files'].drop()
        self.db[db_conf['gridfs_collection'] + '.chuncks'].drop()

    def tearDown(self):
        self.connection.drop_database(self.db)

    def test_add_corpus_method_should_receive_name_and_slug(self):
        returned_corpus = self.store.add_corpus(name='Test Corpus',
                                                slug='test-corpus',
                                                description='spam eggs ham',
                                                owner=u'Álvaro Justen')
        cursor = self.corpora.find()
        self.assertEquals(cursor.count(), 1)
        corpus = cursor[0]
        self.assertEquals(type(returned_corpus), ObjectId)
        del corpus['_id']
        self.assertEquals(corpus['name'], 'Test Corpus')
        self.assertEquals(corpus['slug'], 'test-corpus')
        self.assertEquals(corpus['documents'], [])
        self.assertEquals(corpus['description'], u'spam eggs ham')
        self.assertEquals(corpus['owner'], u'Álvaro Justen')
        self.assertIn('date created', corpus)
        self.assertEquals(type(corpus['date created']), datetime.datetime)
        self.assertEquals(type(corpus['date last modified']), datetime.datetime)
        self.assertEquals(corpus['date last modified'], corpus['date created'])

    def test_list_corpora_should_return__id_name_and_slug(self):
        number_of_corpora = 10
        for i in range(number_of_corpora):
            self.store.add_corpus(name='Test Corpus ' + str(i),
                                  slug='test-corpus-' + str(i),
                                  description='spam eggs ham',
                                  owner='me')
        corpora = self.store.list_corpora()
        self.assertEquals(len(corpora), number_of_corpora)
        for i in range(number_of_corpora):
            self.assertIn('_id', corpora[i])
            self.assertEquals(corpora[i]['name'], 'Test Corpus ' + str(i))
            self.assertEquals(corpora[i]['description'], 'spam eggs ham')
            self.assertEquals(corpora[i]['slug'], 'test-corpus-' + str(i))
            self.assertEquals(corpora[i]['documents'], [])

    def test_find_corpus_by_slug_should_return_a_dict_with_corpus_info_or_None(self):
        self.assertEquals(self.store.find_corpus_by_slug('test-corpus'), None)
        self.store.add_corpus(name='Test Corpus', slug='test-corpus',
                              description='spam eggs ham',
                              owner='me')
        corpus = self.store.find_corpus_by_slug('test-corpus')
        self.assertEquals(type(corpus), dict)
        self.assertIn('_id', corpus)
        self.assertEquals(corpus['name'], 'Test Corpus')
        self.assertEquals(corpus['slug'], 'test-corpus')
        self.assertEquals(corpus['description'], 'spam eggs ham')
        self.assertEquals(corpus['documents'], [])

    def test_find_corpus_by_docid_should_return_a_dict_with_corpus_info_or_None(self):
        self.assertEquals(self.store.find_corpus_by_docid('dummy'), None)
        corpus_id = self.store.add_corpus(name='Test Corpus', slug='test-corpus',
                                          description='ham eggs spam',
                                          owner='me')
        corpus = self.store.find_corpus_by_docid(corpus_id)
        self.assertEquals(type(corpus), dict)
        self.assertEquals(corpus['_id'], corpus_id)
        self.assertEquals(corpus['name'], 'Test Corpus')
        self.assertEquals(corpus['slug'], 'test-corpus')
        self.assertEquals(corpus['description'], 'ham eggs spam')
        self.assertEquals(corpus['documents'], [])
