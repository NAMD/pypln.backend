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
ELASTICSEARCH_CONFIG = {
    'hosts': ['127.0.0.1', '172.16.4.46', '172.16.4.52'],
}

try:
    from local_config import *
except ImportError:
    pass
