import os

from decouple import config, Csv

try:
    import urlparse
except ImportError:
    import urllib.parse as urlparse


def parse_url(url):
    urlparse.uses_netloc.append('mongodb')
    urlparse.uses_netloc.append('celery')
    url = urlparse.urlparse(url)

    path = url.path[1:]
    path = path.split('?', 2)[0]

    return {
        'database': path or '',
        'port': url.port or '',
        'host': url.hostname or '',
        'user': url.username,
        'password': url.password,
    }

    return config

MONGODB_CONFIG = config('MONGODB_CONFIG',
            default='mongodb://localhost:27017/pypln_dev', cast=parse_url)
MONGODB_CONFIG['collection'] =  config('MONGO_COLLECTION', default='analysis')
MONGODB_CONFIG['gridfs_collection'] = config('GRIDFS_COLLECTION', default='files')

ELASTICSEARCH_CONFIG = {
    'hosts': config('ELASTICSEARCH_HOSTS',
        default='127.0.0.1,172.16.4.46,172.16.4.52', cast=Csv())
}

CELERY_BROKER_CONFIG = config('CELERY_CONFIG',
        default='amqp://guest:guest@localhost:5672', cast=parse_url)

BROKER_URL = 'amqp://{}:{}@{}:{}//'.format(
        CELERY_BROKER_CONFIG['user'], CELERY_BROKER_CONFIG['password'],
        CELERY_BROKER_CONFIG['host'], CELERY_BROKER_CONFIG['port'])

CELERY_RESULT_BACKEND = 'mongodb://{}:{}'.format(MONGODB_CONFIG['host'],
        MONGODB_CONFIG['port'])

CELERY_DEFAULT_QUEUE = "pypln"
CELERY_QUEUE_NAME = "pypln"
