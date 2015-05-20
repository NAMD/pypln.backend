import os
import ConfigParser
def get_store_config():
    config_filename = os.path.expanduser('~/.pypln_store_config')
    defaults = {'host': 'localhost',
                'port': '27017',
                'database': 'pypln_dev',
                'gridfs_collection': 'files',
    }
    config = ConfigParser.ConfigParser(defaults=defaults)
    config.add_section('store')
    config.read(config_filename)
    store_config = dict(config.items('store'))
    # The database port needs to be an integer, but ConfigParser will treat
    # everything as a string unless you use the specific method to retrieve the
    # value.
    store_config['port'] = config.getint('store', 'port')
    return store_config

MONGODB_CONFIG = get_store_config()

def get_broker_config():
    defaults = {
        "host": "localhost",
        "port": "5672",
    }
    celery_config = ConfigParser.ConfigParser(defaults=defaults)
    celery_config.add_section('broker')
    celery_config.read(os.path.expanduser('~/.pypln_celery_config'))
    return dict(celery_config.items('broker'))

CELERY_BROKER_CONFIG = get_broker_config()

BROKER_URL = 'amqp://guest:guest@{}:{}//'.format(
        CELERY_BROKER_CONFIG['host'], CELERY_BROKER_CONFIG['port'])

CELERY_RESULT_BACKEND = 'mongodb://{}:{}'.format(MONGODB_CONFIG['host'],
        MONGODB_CONFIG['port'])
try:
    from local_config import *
except ImportError:
    pass
