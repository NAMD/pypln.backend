# coding: utf-8

from datetime import datetime
from unicodedata import normalize
from pymongo import Connection
from gridfs import GridFS


def slug(text, encoding='utf-8',
         permitted_chars='abcdefghijklmnopqrstuvwxyz0123456789-'):
    if isinstance(text, str):
        text = text.decode(encoding or 'ascii')
    clean_text = text.strip().replace(' ', '-').lower()
    while '--' in clean_text:
        clean_text = clean_text.replace('--', '-')
    ascii_text = normalize('NFKD', clean_text).encode('ascii', 'ignore')
    strict_text = map(lambda x: x if x in permitted_chars else '', ascii_text)
    return ''.join(strict_text)

def now():
    '''Return a normalized datetime.datetime.now()

    Need this hack because MongoDB does not store microseconds'''
    date = datetime.now()
    return datetime(date.year, date.month, date.day, date.hour, date.minute,
                    date.second, 0)

class Object(object):
    def __init__(self, **kwargs):
        if '_id' in kwargs:
            setattr(self, '_id', kwargs['_id'])
        else:
            setattr(self, '_id', None)
        for field_name, default_value in self.fields.iteritems():
            if hasattr(default_value, '__call__'):
                default_value = default_value()
            setattr(self, field_name, default_value)
        for key, value in kwargs.iteritems():
            if key in self.fields.keys():
                setattr(self, key, value)

    def save(self):
        for field in self.required_fields:
            if not getattr(self, field) and \
               field not in self.auto_value_fields.keys():
                raise RuntimeError('Field "{}" is required'.format(field))
        data = {}
        for field_name in self.fields.keys():
            data[field_name] = getattr(self, field_name)
        for field_name, update_callable in self.auto_value_fields.iteritems():
            data[field_name] = update_callable(self)
            setattr(self, field_name, data[field_name])
        if self._id is None:
            self._id = self._collection.insert(data)
        else:
            data['_id'] = self._id
            self._collection.update({'_id': self._id}, data)

class ObjectStore(object):
    def __init__(self, store, collection, class_):
        self._store = store
        self._collection = collection
        self._class = class_
        for index in class_.indexes:
            self._collection.ensure_index(index)

    def _make_object(self, **kwargs):
        obj = self._class(**kwargs)
        obj._collection = self._collection
        obj._store = self._store
        return obj

    def __call__(self, **kwargs):
        return self._make_object(**kwargs)

    def __getattr__(self, attribute):
        if attribute.startswith('find_by_'):
            key = attribute[8:]
            if key == 'id':
                key = '_id'
                #TODO: check if the id has been passed as a ObjectID. If not convert it
            def find(value):
                data = self._collection.find_one({key: value})
                if data is None:
                    return None
                else:
                    return self._make_object(**data)
            return find
        else:
            raise AttributeError

    @property
    def all(self):
        return (self._make_object(**obj) for obj in self._collection.find())

class Corpus(Object):
    fields = {'name': '',
              'slug': '',
              'description': '',
              'owner': '',
              'private': False,
              'date_created': lambda: now(),
              'last_modified': None,}
    #TODO: we need a way to get document size(plain text, maybe total storage related to the doc) and blob size for display
    indexes = ['slug', 'owner', 'date_created', 'last_modified']
    required_fields = ['name']
    auto_value_fields = {'last_modified': lambda obj: now(),
                         'slug': lambda obj: slug(obj.name),}

class Document(Object):
    fields = {'filename': '',
              'slug': '',
              'owner': '',
              'corpora': lambda: [],
              'date_created': lambda: now(),}
    indexes = ['slug', 'filename', 'owner', 'date_created', 'corpora']
    required_fields = ['filename']
    auto_value_fields = {'slug': lambda obj: slug(obj.filename),}

    def set_blob(self, blob):
        if self._id is None:
            raise RuntimeError('You need to save document before setting its'
                               ' blob')
        self._store._gridfs.put(blob, filename=self._id)

    def get_blob(self):
        if self._id is None:
            raise RuntimeError('You need to save document before setting its'
                               ' blob')
        fp = self._store._gridfs.get_last_version(filename=self._id)
        return fp.read()

class Analysis(Object):
    fields = {'name': '',
              'value': '',
              'document': lambda: [],
              'date_created': lambda: now(),}
    indexes = ['name', 'value', 'document']
    required_fields = ['name', 'value']
    auto_value_fields = {}

class MongoDBStore(object):
    """
    `<https://github.com/NAMD/pypln/wiki/Document-Store-Design>`_
    """
    def __init__(self, **config):
        self._connection = Connection(host=config['host'], port=config['port'],
                                      safe=True)
        #TODO: implement username and password
        self._db = self._connection[config['database']]
        self._documents = self._db[config['document_collection']]
        self._corpora = self._db[config['corpora_collection']]
        self._analysis = self._db[config['analysis_collection']]
        self._gridfs = GridFS(self._db, config['gridfs_collection'])
        self.Corpus = ObjectStore(self, self._corpora, Corpus)
        self.Document = ObjectStore(self, self._documents, Document)
        self.Analysis = ObjectStore(self, self._analysis, Analysis)
