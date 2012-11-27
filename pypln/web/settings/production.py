#
# Copyright 2012 NAMD-EMAP-FGV
#
# This file is part of PyPLN. You can get more information at: http://pypln.org/.
#
# PyPLN is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# PyPLN is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with PyPLN.  If not, see <http://www.gnu.org/licenses/>.

from base import *
import os

ADMINS = [
    #TODO: define admin e-mail
]

MANAGERS = ADMINS

SERVE_MEDIA = False

pgpass_file_path = os.path.expanduser("~/.pgpass")
secret_key_file_path = os.path.expanduser("~/.secret_key")

with open(secret_key_file_path, 'r') as secret_key_file:
    SECRET_KEY = secret_key_file.read().strip()

with open(pgpass_file_path, 'r') as pgpass_file:
    pg_credentials = pgpass_file.read().strip()

db_host, db_port, db_name, db_user, db_password = pg_credentials.split(":")

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql_psycopg2",
        "NAME": db_name,
        "USER": db_user,
        "PASSWORD": db_password,
        "HOST": db_host,
        "PORT": db_port,
    }
}

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
