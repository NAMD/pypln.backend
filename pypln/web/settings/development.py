from base import *

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
