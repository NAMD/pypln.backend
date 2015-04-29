MONGODB_CONFIG = {
    'host': 'localhost',
    'port': 27017,
    'database': 'pypln_dev',
    'gridfs_collection': 'files',
}

try:
    from local_config import *
except ImportError:
    pass
