# coding: utf-8
#
# Copyright 2012 NAMD-EMAP-FGV
#
# This file is part of PyPLN. You can get more information at: http://pypln.org/.
#
# PyPLN is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# PyPLN is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with PyPLN.  If not, see <http://www.gnu.org/licenses/>.

import pickle
import unittest

from bson import Binary
import pymongo

from pypln.backend.mongodict_adapter import MongoDictAdapter



class TestMongoDictAdapter(unittest.TestCase):
    db_name = 'test_mongodictbyid'

    def setUp(self):
        self.fake_id = '1234'
        self.document = MongoDictAdapter(self.fake_id, database=self.db_name)
        self.db = pymongo.Connection()[self.db_name]

    def tearDown(self):
        self.db.main.remove({})

    @classmethod
    def tearDownClass(cls):
        pymongo.MongoClient().drop_database(cls.db_name)

    def test_creating_a_new_key_should_saved_the_information(self):
        self.document['new_key'] = 'value'
        stored_value = self.db.main.find_one(
            {'_id': 'id:{}:new_key'.format(self.fake_id)})
        self.assertIsNotNone(stored_value)
        # This decodes the value with the defaults for MongoDict
        decoded_value = pickle.loads(str(stored_value['v']))
        self.assertEqual(decoded_value, 'value')

    def test_reading_an_existing_key_should_read_saved_information(self):
        encoded_value = Binary(pickle.dumps(
            'value', protocol=pickle.HIGHEST_PROTOCOL))

        self.db.main.insert(
                {'_id': 'id:{}:key'.format(self.fake_id), 'v': encoded_value})

        self.assertEqual(self.document['key'], 'value')

    def test_deleting_an_existing_key_should_delete_saved_information(self):
        encoded_value = Binary(pickle.dumps(
            'value', protocol=pickle.HIGHEST_PROTOCOL))

        self.db.main.insert(
                {'_id': 'id:{}:key'.format(self.fake_id), 'v': encoded_value})

        self.assertEqual(self.document['key'], 'value')
        del self.document['key']

        stored_value = self.db.main.find_one(
            {'_id': 'id:{}:key'.format(self.fake_id)})
        self.assertIsNone(stored_value)

    def test_iterating_through_keys_does_not_bring_keys_from_other_docs(self):
        self.document['key_1'] = 1
        self.document['key_2'] = 2
        other_document = MongoDictAdapter('other_id', database=self.db_name)
        other_document['other_key'] = 3
        keys = [k for k in self.document]

        self.assertIn('key_1', keys)
        self.assertIn('key_2', keys)
        self.assertNotIn('key_3', keys)

        self.assertEquals(['key_1', 'key_2'], self.document.keys())

    def test_clear_should_not_remove_keys_for_other_docs(self):
        self.document['key_1'] = 1
        self.document['key_2'] = 2
        other_document = MongoDictAdapter('other_id', database=self.db_name)
        other_document['other_key'] = 3

        self.document.clear()

        with self.assertRaises(KeyError):
            self.document['key_1']
            self.document['key_2']

        self.assertEqual(other_document['other_key'], 3)

    def test_return_correct_length(self):
        self.document['key_1'] = 1
        self.document['key_2'] = 2
        other_document = MongoDictAdapter('other_id', database=self.db_name)
        other_document['other_key'] = 3

        self.assertEquals(len(self.document), 2)

    def test_contains(self):
        self.document['key'] = 1
        self.assertIn('key', self.document)
        self.assertNotIn('inexistent_key', self.document)

    def test_has_key(self):
        self.document['key'] = 1
        self.assertTrue(self.document.has_key('key'))
        self.assertFalse(self.document.has_key('inexistent_key'))
