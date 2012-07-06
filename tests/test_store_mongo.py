# coding: utf-8

import unittest
import pymongo
from gridfs import GridFS
from pypln.stores.mongo import MongoDBStore


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

    def test_add_corpus_method_should_receive_name_and_slug(self):
        self.store.add_corpus(name='Test Corpus', slug='test-corpus')
        cursor = self.corpora.find()
        self.assertEquals(cursor.count(), 1)
        corpus = cursor[0]
        del corpus['_id']
        expected_corpus = {'name': 'Test Corpus', 'slug': 'test-corpus',
                           'documents': []}
        self.assertEquals(corpus, expected_corpus)

    def test_list_corpora_should_return__id_name_and_slug(self):
        number_of_corpora = 10
        for i in range(number_of_corpora):
            self.store.add_corpus(name='Test Corpus ' + str(i),
                                  slug='test-corpus-' + str(i))
        corpora = self.store.list_corpora()
        self.assertEquals(len(corpora), number_of_corpora)
        for i in range(number_of_corpora):
            self.assertIn('_id', corpora[i])
            self.assertEquals(corpora[i]['name'], 'Test Corpus ' + str(i))
            self.assertEquals(corpora[i]['slug'], 'test-corpus-' + str(i))
            self.assertEquals(corpora[i]['documents'], [])

    def test_find_corpus_by_slug_should_return_a_dict_with_corpus_info_or_None(self):
        self.assertEquals(self.store.find_corpus_by_slug('test-corpus'), None)
        self.store.add_corpus(name='Test Corpus', slug='test-corpus')
        corpus = self.store.find_corpus_by_slug('test-corpus')
        self.assertEquals(type(corpus), dict)
        self.assertIn('_id', corpus)
        self.assertEquals(corpus['name'], 'Test Corpus')
        self.assertEquals(corpus['slug'], 'test-corpus')
        self.assertEquals(corpus['documents'], [])
