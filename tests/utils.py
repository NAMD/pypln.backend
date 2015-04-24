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

from random import randrange
import unittest
import pymongo

from pypln.backend.mongodict_adapter import MongoDictAdapter
from pypln.backend.celery_app import app


class TaskTest(unittest.TestCase):
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




def random_string(min_size=10, max_size=100):
    result = []
    for i in range(randrange(min_size, max_size)):
        result.append(chr(randrange(65, 91)))
    return ''.join(result)

default_config = {'store': {'host': 'localhost', 'port': 27017,
                            'database': 'pypln-test',
                            'analysis_collection': 'analysis',
                            'gridfs_collection': 'files',
                            'monitoring_collection': 'monitoring',},
                  'monitoring interval': 60,
}
