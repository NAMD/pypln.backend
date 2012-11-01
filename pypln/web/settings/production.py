from base import *

raise ImportError("We are not ready for a production deploy yet.")

ADMINS = [
    #TODO: define admin e-mail
]

MANAGERS = ADMINS

#TODO: Read database settings (user, passwd etc) from a file on the server
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql_psycopg2",
        "NAME": "",
        "USER": "",
        "PASSWORD": "",
        "HOST": "",
        "PORT": "",
    }
}

SECRET_KEY = "" #TODO: Read SECRET_KEY from a file on the server

#TODO: read router configuration from a config file (issue #14)
ROUTER_API = 'tcp://127.0.0.1:5555'
ROUTER_BROADCAST = 'tcp://127.0.0.1:5555'
ROUTER_TIMEOUT = 5

CONFIGURATION = get_config_from_router(ROUTER_API)
if CONFIGURATION is None:
    MONGODB_CONFIG = {'host': 'localhost',
                      'port': 27017,
                      'database': 'pypln',
                      'gridfs_collection': 'files',
                      'analysis_collection': 'analysis',
                      'monitoring_collection': 'monitoring',
    }
else:
    MONGODB_CONFIG = CONFIGURATION['store']
