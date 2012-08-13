# coding: utf-8

import unittest
import datetime
from pymongo import Connection
from gridfs import GridFS
from mongodict import MongoDict
from pypln.stores.mongo import MongoDBStore
from bson import ObjectId
from .utils import default_config


class TestMongoStore(unittest.TestCase):
    def setUp(self):
        #TODO: unify config
        self.db_conf = db_conf = default_config['db']
        self.connection = Connection(host=db_conf['host'],
                                     port=db_conf['port'])
        self.db = self.connection[db_conf['database']]
        self.documents = self.db[db_conf['analysis_collection']]
        self.gridfs = GridFS(self.db, db_conf['gridfs_collection'])
        self.documents.drop()
        self.db[db_conf['gridfs_collection'] + '.files'].drop()
        self.db[db_conf['gridfs_collection'] + '.chuncks'].drop()
        self.store = MongoDBStore(**db_conf)

    def tearDown(self):
        self.connection.drop_database(self.db)

    def test_retrieve_should_raise_KeyError_if_data_does_not_exist(self):
        job_data = {
                'worker_input': 'document',
                'worker_requires': ['bla'],
                'worker_output': 'document',
                'worker_requires': [''],
                'worker': 'test',
                'data': {'id': '123'},
        }
        with self.assertRaises(KeyError):
            result = self.store.retrieve(job_data)

    def test_save_and_retrieve(self):
        job_data = {
                'worker_input': 'document',
                'worker_provides': ['spam', 'eggs'],
                'worker_output': 'document',
                'worker_requires': ['spam', 'eggs'],
                'worker': 'test',
                'data': {'id': '123'},
                'result': {'bla': 123, 'spam': 42, 'eggs': 'ham'}
        }
        self.store.save(job_data)
        expected = {'spam': 42, 'eggs': 'ham'}
        result = self.store.retrieve(job_data)
        self.assertEqual(expected, result)
