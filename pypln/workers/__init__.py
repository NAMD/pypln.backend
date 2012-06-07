# coding: utf-8

import sys
from os.path import dirname, basename
from glob import glob
from importlib import import_module


__all__ = ['available', 'wrapper']
current_dir = dirname(__file__)
required_objects = ['__meta__', 'main']
required_meta = ['from', 'requires', 'to', 'provides']

available = {}
sys.path.insert(0, current_dir)
for filename in glob('{}/*.py'.format(current_dir)):
    worker = basename(filename[:-3])
    if worker != '__init__':
        worker_module = import_module(worker)
        worker_objects = dir(worker_module)
        for obj in required_objects:
            if obj not in worker_objects:
                break
        else:
            meta_obj = getattr(worker_module, '__meta__')
            meta_keys = meta_obj.keys()
            for meta in required_meta:
                if meta not in meta_keys:
                    break
            else:
                __all__.append(worker)
                available[worker] = {'main': getattr(worker_module, 'main'),
                                     'from': meta_obj['from'],
                                     'requires': meta_obj['requires'],
                                     'to': meta_obj['to'],
                                     'provides': meta_obj['provides'],
                                    }

def wrapper(child_connection):
    #TODO: should receive the document or database's configuration?
    #      Note that if a worker should process a big document or an entire
    #      corpus, it's better to received database's configuration and pass to
    #      worker only an lazy iterator for the collection (pymongo's cursor)
    #TODO: create documentation about object type returned by worker (strings
    #      must be unicode)
    #TODO: add the possibility to create workers that are executables (they
    #      receive data as JSON in stdin and put the result as JSON in stdout),
    #      so we can create workers in C, Perl, Ruby etc.
    worker, document = child_connection.recv()
    result = available[worker]['main'](document)
    child_connection.send(result)
