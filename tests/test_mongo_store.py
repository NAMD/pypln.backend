# coding: utf-8

import unittest
import datetime
import md5

import gridfs

from pymongo import Connection
from mongodict import MongoDict
from pypln.backend.mongo_store import MongoDBStore
from bson import ObjectId

from .utils import default_config, monitoring_sample, random_string


class TestMongoStore(unittest.TestCase):
    def setUp(self):
        self.db_conf = db_conf = default_config['store']
        self.connection = Connection(host=db_conf['host'],
                                     port=db_conf['port'])
        self.connection.drop_database(db_conf['database'])
        self.db = self.connection[db_conf['database']]
        self.monitoring = self.db[db_conf['monitoring_collection']]
        self.gridfs = gridfs.GridFS(self.db, db_conf['gridfs_collection'])
        self.db[db_conf['gridfs_collection'] + '.files'].drop()
        self.db[db_conf['gridfs_collection'] + '.chuncks'].drop()
        self.mongodict = MongoDict(host=db_conf['host'], port=db_conf['port'],
                                   database=db_conf['database'],
                                   collection=db_conf['analysis_collection'])
        self.store = MongoDBStore(**db_conf)

    def tearDown(self):
        self.connection.drop_database(self.db)

    def test_retrieve_should_raise_ValueError_if_missing_id(self):
        object_id = ObjectId("5089d72b7af8d6fc1a5a7b91")
        # Extractor worker needs '_id'
        info = {'data': {'id': 123}, 'worker': 'Extractor',
                'worker_requires': []}
        with self.assertRaises(ValueError):
            self.store.retrieve(info)
        info['data']['_id'] = object_id # fix it
        with self.assertRaises(gridfs.NoFile):
            # no problem with ['data']['id'] but with gridfs file
            self.store.retrieve(info)

        # other workers must have 'id'
        info = {'data': {'_id': object_id}, 'worker': 'other',
                'worker_requires': []}
        with self.assertRaises(ValueError):
            self.store.retrieve(info)
        info['data']['id'] = 123 # fix it
        self.store.retrieve(info) # no problem

    def test_retrieve_from_Extractor_should_return_file_on_gridfs(self):
        start_datetime = datetime.datetime.utcnow()
        data = 'This is just a test.\nPython rules. Álvaro Justen.\n'
        my_file = self.gridfs.new_file(filename='spam.txt')
        my_file.write(data)
        my_file.close()
        after_datetime = datetime.datetime.utcnow()

        info = {'data': {'id': 456, '_id': my_file._id}, 'worker': 'Extractor',
                'worker_requires': []}
        result = self.store.retrieve(info)
        self.assertIn('upload_date', result)
        self.assertIn('length', result)
        self.assertIn('filename', result)
        self.assertIn('contents', result)
        self.assertIn('md5', result)

        self.assertTrue(result['upload_date'] > start_datetime)
        self.assertTrue(result['upload_date'] < after_datetime)
        self.assertEqual(result['length'], len(data))
        self.assertIn(result['filename'], 'spam.txt')
        self.assertIn(result['contents'], data)
        self.assertIn(result['md5'], md5.md5(data).hexdigest())

    def test_retrieve_from_other_workers_should_return_info_from_mongodict(self):
        data = random_string()
        self.mongodict['id:789:property_1'] = data

        info = {'data': {'id': 789, '_id': 'eggs'}, 'worker': 'NotExtractor',
                'worker_requires': ['property_1']}
        result = self.store.retrieve(info)
        expected = {'property_1': data, '_missing': []}
        self.assertEquals(result, expected)

    def test_retrieve_from_other_workers_should_not_return_keys_that_dont_exist(self):
        data_1, data_2 = random_string(), random_string()
        self.mongodict['id:789:property_1'] = data_1
        self.mongodict['id:789:property_4'] = data_2

        info = {'data': {'id': 789, '_id': 'eggs'}, 'worker': 'NotExtractor',
                'worker_requires': ['property_2', 'property_3', 'property_4']}
        result = self.store.retrieve(info)
        expected = {'property_4': data_2,
                    '_missing': ['property_2', 'property_3']}
        self.assertEquals(result, expected)

    def test_save_expect_data_id(self):
        info = {'data': {}, 'worker': 'SomeWorker', 'worker_requires': [],
                'worker_result': {}}
        with self.assertRaises(ValueError):
            self.store.save(info)

    def test_save_must_save_every_key_on_worker_result_in_mongodict(self):
        info = {'data': {'id': 42}, 'worker': 'SomeWorker',
                'worker_requires': [],
                'worker_result': {'this': 'is', 'a': 'test'}}
        self.store.save(info)
        self.assertIn('id:42:this', self.mongodict)
        self.assertIn('id:42:a', self.mongodict)
        self.assertIn('id:42:_properties', self.mongodict)
        self.assertEqual(self.mongodict['id:42:this'], 'is')
        self.assertEqual(self.mongodict['id:42:a'], 'test')
        self.assertEqual(set(self.mongodict['id:42:_properties']),
                         set(['this', 'a']))

        # if there are properties, should add to _properties list
        more_info = {'data': {'id': 42}, 'worker': 'OtherWorker',
                     'worker_requires': [],
                     'worker_result': {'spam': 123, 'eggs': 3.14, 'this': 'a'}}
        self.store.save(more_info)
        self.assertIn('id:42:this', self.mongodict)
        self.assertIn('id:42:a', self.mongodict)
        self.assertIn('id:42:spam', self.mongodict)
        self.assertIn('id:42:eggs', self.mongodict)
        self.assertIn('id:42:_properties', self.mongodict)
        self.assertEqual(self.mongodict['id:42:this'], 'a')
        self.assertEqual(self.mongodict['id:42:a'], 'test')
        self.assertEqual(self.mongodict['id:42:spam'], 123)
        self.assertEqual(self.mongodict['id:42:eggs'], 3.14)
        self.assertEqual(set(self.mongodict['id:42:_properties']),
                         set(['this', 'a', 'spam', 'eggs']))
        self.assertEqual(len(self.mongodict['id:42:_properties']), 4)

    def test_save_monitoring_information_should_just_add_info_to_a_collection(self):
        self.assertEqual(self.monitoring.count(), 0)
        self.store.save_monitoring(monitoring_sample)
        self.assertEqual(self.monitoring.count(), 1)
        sample = self.monitoring.find_one()
        self.assertEqual(sample, monitoring_sample)
