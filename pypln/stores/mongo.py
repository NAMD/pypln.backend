# coding: utf-8

import datetime
from pymongo import Connection
from gridfs import GridFS


class MongoDBStore(object):
    def __init__(self, **config):
        self._connection = Connection(host=config['host'], port=config['port'])
        #TODO: implement username and password
        self._db = self._connection[config['database']]
        self._documents = self._db[config['document_collection']]
        self._corpora = self._db[config['corpora_collection']]
        self._gridfs = GridFS(self._db, config['gridfs_collection'])

    def add_corpus(self, name, slug, description, owner):
        date = datetime.datetime.now()
        return self._corpora.insert({'name': name, 'slug': slug,
                                     'documents': [], 'owner': owner,
                                     'description': description,
                                     'date created': date,
                                     'date last modified': date,})

    def list_corpora(self):
        return list(self._corpora.find())

    def find_corpus_by_slug(self, slug):
        results = list(self._corpora.find({'slug': slug}))
        if not results:
            return None
        return results[0]

    def find_corpus_by_docid(self, slug):
        results = list(self._corpora.find({'_id': slug}))
        if not results:
            return None
        return results[0]
