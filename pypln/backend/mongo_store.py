# coding: utf-8

from pymongo import Connection
from gridfs import GridFS
from bson import ObjectId
from mongodict import MongoDict


class MongoDBStore(object):
    '''Store PyPLN workers' analysis in MongoDB, using MongoDict'''

    def __init__(self, **config):
        host, port, database = config['host'], config['port'], \
                               config['database']
        self._connection = Connection(host, port)
        self._db = self._connection[database]
        if 'username' in config and 'password' in config:
           self._db.authenticate(username, password)
        self._dict = MongoDict(host=host, port=port, database=database,
                               collection=config['analysis_collection'])
        #TODO: use auth on mongodict
        self._monitoring = self._db[config['monitoring_collection']]
        self._gridfs = GridFS(self._db, config['gridfs_collection'])

    def retrieve(self, info):
        '''Retrieve data to pass to `WorkerClass.process`

        `info` has keys 'worker', 'worker_requires' and 'data':
            - 'data' comes from pipeline data
            - 'worker' is the worker name
            - 'worker_requires' is 'requires' attribute of WorkerClass
        '''
        data = info['data']

        result = {'_missing': []}
        if info['worker'] == 'Extractor':
            if '_id' not in data:
                raise ValueError('Invalid job data: missing "_id"')
            file_data = self._gridfs.get(ObjectId(data['_id']))
            result = {'length': file_data.length,
                      'md5': file_data.md5,
                      'filename': file_data.filename,
                      'upload_date': file_data.upload_date,
                      'contents': file_data.read()}
        else:
            if 'id' not in data:
                raise ValueError('Invalid job data: missing "id"')
            for key in info['worker_requires']:
                new_key = 'id:{}:{}'.format(data['id'], key)
                try:
                    result[key] = self._dict[new_key]
                except KeyError:
                    result['_missing'].append(key)
        return result

    def save(self, info):
        '''Save information returned by `WorkerClass.process`

        `info` has keys 'worker', 'worker_requires', 'worker_result' and 'data':
            - 'data' comes from pipeline data
            - 'worker' is the worker name
            - 'worker_requires' is 'requires' attribute of WorkerClass
            - 'worker_result' is what WorkerClass.process returned
        '''
        data = info['data']
        worker_result = info['worker_result']
        if 'id' not in data:
            raise ValueError('Invalid job data: missing "id"')

        # insert results
        for key, value in worker_result.items():
            new_key = 'id:{}:{}'.format(data['id'], key)
            self._dict[new_key] = worker_result[key]

        # update property list for this document
        properties_key = 'id:{}:_properties'.format(data['id'])
        all_properties = self._dict.get(properties_key, []) + \
                         worker_result.keys()
        self._dict[properties_key] = list(set(all_properties))

    def save_monitoring(self, info):
        '''Save broker's monitoring information'''
        self._monitoring.insert(info)
