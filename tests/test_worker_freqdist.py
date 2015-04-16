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

import unittest

import pymongo

from pypln.backend.mongodict_adapter import MongoDictAdapter
from pypln.backend.workers import FreqDist
from pypln.backend.celery_app import app



class TestFreqDistWorker(unittest.TestCase):
    db_name = 'test_pypln_backend'

    def setUp(self):
        app.conf.update(CELERY_ALWAYS_EAGER=True)
        self.fake_id = '1234'
        self.document = MongoDictAdapter(self.fake_id, database=self.db_name)
        self.db = pymongo.Connection()[self.db_name]

    def tearDown(self):
        self.db.main.remove({})

    @classmethod
    def tearDownClass(cls):
        pymongo.MongoClient().drop_database(cls.db_name)

    def test_freqdist_should_return_a_list_of_tuples_with_frequency_distribution(self):
        fake_id = '1234'
        tokens = ['The', 'sky', 'is', 'blue', ',', 'the', 'sun', 'is',
                  'yellow', '.']

        expected_fd =  [('is', 2), ('the', 2), ('blue', 1), ('sun', 1),
                ('sky', 1), (',', 1), ('yellow', 1), ('.', 1)]


        # This is just preparing the expected input in the database
        self.document['tokens'] = tokens

        FreqDist().delay(fake_id)

        resulting_fd = self.document['freqdist']

        self.assertEqual(resulting_fd, expected_fd)
