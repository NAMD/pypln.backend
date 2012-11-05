from base import *
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

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": os.path.join(PROJECT_ROOT, "dev.db"),
        "USER": "",
        "PASSWORD": "",
        "HOST": "",
        "PORT": "",
    }
}

DEBUG = True
TEMPLATE_DEBUG = True
# tells Pinax to serve media through the staticfiles app.
SERVE_MEDIA = True

# Make this unique, and don't share it with anybody.
SECRET_KEY = "r9^6-zqrk-$uyu96z!$sakf%^ng!w&4^d8qj@t#taxtgi+a1p9"

EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_DEBUG = True

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
