# coding: utf-8

from pymongo import Connection
from gridfs import GridFS
from bson import ObjectId
from mongodict import MongoDict


class MongoDBStore(object):
    def __init__(self, host, port, database, analysis_collection,
                 gridfs_collection, monitoring_collection, username=None,
                 password=None):
        self._connection = Connection(host, port)
        self._db = self._connection[database]
        if username is not None and password is not None:
           self._db.authenticate(username, password)
        self._dict = MongoDict(host=host, port=port, database=database,
                               collection=analysis_collection)
        #TODO: use auth on mongodict
        self._monitoring = self._db[monitoring_collection]
        self._gridfs = GridFS(self._db, gridfs_collection)

    def save(self, data):
        worker_input = data['worker_input']
        worker_output = data['worker_output']
        worker_provides = data['worker_provides']
        job_data = data['data']
        result = data['result']
        if worker_output == 'document':
            if 'id' not in job_data:
                raise ValueError('Invalid job data')
            if worker_input == 'gridfs-file':
                if '_id' not in job_data:
                    raise ValueError('Invalid job data')
            total = []
            for key in worker_provides:
                if key in result:
                    new_key = 'id:{}:{}'.format(job_data['id'], key)
                    self._dict[new_key] = result[key]
                    total.append(key)
            analysis_key = 'id:{}:analysis'.format(job_data['id'])
            try:
                self._dict[analysis_key] += total
                #TODO: change to 'push'
            except KeyError:
                self._dict[analysis_key] = total

    def save_monitoring(self, data):
        self._monitoring.insert(data)

    def retrieve(self, data):
        worker_input = data['worker_input']
        worker_requires = data['worker_requires']
        job_data = data['data']

        result = {}
        if worker_input == 'document':
            if 'id' not in job_data:
                raise ValueError('Invalid job data')
            for key in worker_requires:
                new_key = 'id:{}:{}'.format(job_data['id'], key)
                result[key] = self._dict[new_key]
        elif worker_input == 'gridfs-file':
            if '_id' not in job_data:
                raise ValueError('Invalid job data')
            file_data = self._gridfs.get(ObjectId(job_data['_id']))
            result = {'length': file_data.length,
                      'md5': file_data.md5,
                      'filename': file_data.filename,
                      'upload_date': file_data.upload_date,
                      'contents': file_data.read()}
        return result
