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

from pypln.backend.celery_app import app
from pypln.backend import config

class ConfigurationError(Exception):
    pass

class TaskTest(unittest.TestCase):
    db_name = config.MONGODB_DBNAME

    def setUp(self):
        app.conf.update(CELERY_ALWAYS_EAGER=True)
        self.db = pymongo.Connection()[self.db_name]
        self.collection = self.db[config.MONGODB_COLLECTION]

    def tearDown(self):
        self.collection.remove({})

    @classmethod
    def setUpClass(cls):
        # Maybe our test runner should set the new database name. For now, this
        # ensures we will not drop the wrong database.
        if not cls.db_name.startswith('test'):
            raise ConfigurationError("The name of the database used to run "
                    "tests needs to start with `test`. This is a safeguard to "
                    "guarantee we don't drop (or polute) the wrong database.")

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
