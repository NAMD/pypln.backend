#!/usr/bin/env python
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

from time import time, asctime
from random import randint, random
from pymongo import Connection


data = \
{'host': {'cpu': {'cpu percent': 4.9, 'number of cpus': 4},
          'memory': {'buffers': 214372352L,
                     'cached': 919220224,
                     'free': 1369661440L,
                     'free virtual': 0,
                     'percent': 65.21955293723627,
                     'real free': 2503254016L,
                     'real percent': 36.433711831634305,
                     'real used': 1434767360L,
                     'total': 3938021376L,
                     'total virtual': 0,
                     'used': 2568359936L,
                     'used virtual': 0},
          'network': {'cluster ip': '127.0.0.1',
                      'interfaces': {'eth0': {'bytes received': 171472224,
                                              'bytes sent': 12556068,
                                              'packets received': 1527830,
                                              'packets sent': 61180},
                                     'eth1': {'bytes received': 74551186,
                                              'bytes sent': 171524,
                                              'packets received': 524231,
                                              'packets sent': 1130},
                                     'lo': {'bytes received': 483510,
                                            'bytes sent': 483510,
                                            'packets received': 4373,
                                            'packets sent': 4373},
                                     'teredo': {'bytes received': 0,
                                                'bytes sent': 0,
                                                'packets received': 0,
                                                'packets sent': 0}}},
          'storage': {'/dev/sda3': {'file system': 'ext4',
                                    'mount point': '/',
                                    'percent used': 70.8,
                                    'total bytes': 399561412608,
                                    'total free bytes': 96656392192,
                                    'total used bytes': 282904956928}},
          'uptime': 17135.324898004532},
 'processes': [{'active workers': 4,
                'cpu percent': 0.0,
                'pid': 5505,
                'resident memory': 7438336,
                'started at': 1339540467.82,
                'type': 'broker',
                'virtual memory': 46899200},
               {'cpu percent': 0.0,
                'data': '...',
                'pid': 5505,
                'resident memory': 7467008,
                'started at': 1339540467.82,
                'type': 'worker',
                'virtual memory': 46899200,
                'worker': 'the worker is a lie'},
               {'cpu percent': 0.0,
                'data': '...',
                'pid': 5505,
                'resident memory': 7471104,
                'started at': 1339540467.82,
                'type': 'worker',
                'virtual memory': 46899200,
                'worker': 'the worker is a lie'},
               {'cpu percent': 0.0,
                'data': '...',
                'pid': 5505,
                'resident memory': 7471104,
                'started at': 1339540467.82,
                'type': 'worker',
                'virtual memory': 46899200,
                'worker': 'the worker is a lie'},
               {'cpu percent': 0.0,
                'data': '...',
                'pid': 5505,
                'resident memory': 7471104,
                'started at': 1339540467.82,
                'type': 'worker',
                'virtual memory': 46899200,
                'worker': 'the worker is a lie'}],
 'timestamp': 1339540468.831705}

def populate_collection():
    db[collection_name].drop()
    collection = db[collection_name]
    print '[{}] Inserting total of {} measures ({} for {} brokers)...'\
            .format(asctime(), measures * brokers, measures, brokers)
    for measure in range(1, measures + 1):
        for broker in range(1, brokers + 1):
            if '_id' in data:
                del data['_id']
            data['host']['network']['cluster ip'] = '192.168.0.{}'.format(broker)
            data['processes'][0]['pid'] = randint(0, 65535)
            data['timestamp'] = start_time + measure * time_between_measures + \
                                random()
            collection.insert(data)
        if measure % 10000 == 0:
            print '  [{}] Inserted {} measures'.format(asctime(),
                    measure * broker)
    print '[{}] Done inserting measures!'.format(asctime())

    print '[{}] Creating index for "host.network.cluster ip"'.format(asctime())
    collection.ensure_index('host.network.cluster ip')
    print '[{}] Done!'.format(asctime())

    print '[{}] Creating index for "timestamp"'.format(asctime())
    collection.ensure_index([('timestamp', -1)])
    print '[{}] Done!'.format(asctime())

database_name = 'pypln'
collection_name = 'monitoring' # WARNING: it'll drop the collection!
brokers = 4
time_between_measures = 60 # seconds
measures = 60 * 24 * 365 # one year!
start_time = time() - (time_between_measures * (measures + 1))
connection = Connection(safe=True)
db = connection[database_name]
collection = db[collection_name]

#populate_collection()

last_time_to_check = time() - 100 * time_between_measures
match = {'timestamp': {'$gt': last_time_to_check}}
selected_fields = {'host.network.cluster ip': 1, 'timestamp': 1}
start_time = time()
broker_ips = list(collection.find(match, {'host.network.cluster ip': 1})\
        .distinct('host.network.cluster ip'))
end_time = time()
total_time = end_time - start_time
print 'Time to get broker IPs: {}. Broker IPs: {}'.format(total_time,
        ', '.join(broker_ips))

print '[{}] Getting last measure for each broker...'.format(asctime())
measures = {}
start_time = time()
for broker_ip in broker_ips:
    match = {'timestamp': {'$gt': last_time_to_check},
             'host.network.cluster ip': broker_ip}
    result = list(collection.find(match).limit(1))
    measures[broker_ip] = result
end_time = time()
total_time = end_time - start_time
print '[{}] Time to get all information: {}'.format(asctime(), total_time)
for broker_ip, measure_list in measures.iteritems():
    print 'Broker: {}, measure: {}'.format(broker_ip, measure_list[0])
connection.close()
