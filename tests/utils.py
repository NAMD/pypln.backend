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

monitoring_sample = \
{'datetime': [2012, 10, 26, 18, 38, 57, 4, 300, -1],
 'host': {'cpu': {'cpu percent': 32.5, 'number of cpus': 4},
          'memory': {'buffers': 22138880L,
                     'cached': 355336192,
                     'free': 94998528L,
                     'free virtual': 0L,
                     'percent': 97.58766341492336,
                     'real free': 472473600L,
                     'real percent': 88.00228409051904,
                     'real used': 3465555968L,
                     'total': 3938029568L,
                     'total virtual': 0L,
                     'used': 3843031040L,
                     'used virtual': 0L},
          'network': {'cluster ip': '127.0.0.1',
                      'interfaces': {'eth0': {'bytes received': 261445920,
                                              'bytes sent': 49557117,
                                              'packets received': 325187,
                                              'packets sent': 282361},
                                     'eth1': {'bytes received': 1021135,
                                              'bytes sent': 17132,
                                              'packets received': 5939,
                                              'packets sent': 103},
                                     'lo': {'bytes received': 8793427,
                                            'bytes sent': 8793427,
                                            'packets received': 33867,
                                            'packets sent': 33867},
                                     'teredo': {'bytes received': 0,
                                                'bytes sent': 234864,
                                                'packets received': 0,
                                                'packets sent': 2937}}},
          'storage': {'/dev/sda3': {'file system': 'ext4',
                                    'mount point': '/',
                                    'percent used': 78.0,
                                    'total bytes': 393723564032,
                                    'total free bytes': 66740322304,
                                    'total used bytes': 306983178240}},
          'uptime': 61796.50727200508},
 'processes': [{'active workers': 0,
                'cpu percent': 0.0,
                'number of workers': 16,
                'pid': 11172,
                'resident memory': 14585856,
                'started at': 1351276733.51,
                'type': 'broker',
                'virtual memory': 180486144},
               {'cpu percent': 0.0,
                'pid': 11179,
                'resident memory': 10543104,
                'started at': 1351276734.96,
                'type': 'worker',
                'virtual memory': 113238016},
               {'cpu percent': 0.0,
                'pid': 11180,
                'resident memory': 10481664,
                'started at': 1351276734.96,
                'type': 'worker',
                'virtual memory': 113238016},
               {'cpu percent': 0.0,
                'pid': 11181,
                'resident memory': 10489856,
                'started at': 1351276734.97,
                'type': 'worker',
                'virtual memory': 113238016},
               {'cpu percent': 0.0,
                'pid': 11182,
                'resident memory': 10493952,
                'started at': 1351276734.97,
                'type': 'worker',
                'virtual memory': 113238016},
               {'cpu percent': 0.0,
                'pid': 11183,
                'resident memory': 10485760,
                'started at': 1351276734.97,
                'type': 'worker',
                'virtual memory': 113238016},
               {'cpu percent': 0.0,
                'pid': 11184,
                'resident memory': 10498048,
                'started at': 1351276734.97,
                'type': 'worker',
                'virtual memory': 113238016},
               {'cpu percent': 0.0,
                'pid': 11185,
                'resident memory': 10510336,
                'started at': 1351276734.97,
                'type': 'worker',
                'virtual memory': 113238016},
               {'cpu percent': 0.0,
                'pid': 11186,
                'resident memory': 10502144,
                'started at': 1351276734.97,
                'type': 'worker',
                'virtual memory': 113238016},
               {'cpu percent': 0.0,
                'pid': 11187,
                'resident memory': 10510336,
                'started at': 1351276734.97,
                'type': 'worker',
                'virtual memory': 113238016},
               {'cpu percent': 0.0,
                'pid': 11188,
                'resident memory': 10588160,
                'started at': 1351276734.97,
                'type': 'worker',
                'virtual memory': 113238016},
               {'cpu percent': 0.0,
                'pid': 11189,
                'resident memory': 10518528,
                'started at': 1351276734.97,
                'type': 'worker',
                'virtual memory': 113238016},
               {'cpu percent': 0.0,
                'pid': 11190,
                'resident memory': 10518528,
                'started at': 1351276734.97,
                'type': 'worker',
                'virtual memory': 113238016},
               {'cpu percent': 0.0,
                'pid': 11191,
                'resident memory': 10616832,
                'started at': 1351276734.97,
                'type': 'worker',
                'virtual memory': 113373184},
               {'cpu percent': 0.0,
                'pid': 11192,
                'resident memory': 10534912,
                'started at': 1351276734.98,
                'type': 'worker',
                'virtual memory': 113373184},
               {'cpu percent': 0.0,
                'pid': 11193,
                'resident memory': 10539008,
                'started at': 1351276734.98,
                'type': 'worker',
                'virtual memory': 113373184},
               {'cpu percent': 0.0,
                'pid': 11194,
                'resident memory': 10543104,
                'started at': 1351276734.98,
                'type': 'worker',
                'virtual memory': 113373184}]}
