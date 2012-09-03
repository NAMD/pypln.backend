# -*- coding: utf-8 -*-
#######################################
########APP Settings ##########
#######################################

# enable debug mode.  Disable this in production!
DEBUG = True

# Secret key for app encryption.
# Simple way to generate a random secret key:
#
#    python -c "print repr(__import__('os').urandom(40))"
#SQLALCHEMY_DATABASE_URI = 'postgresql://user:password@127.0.0.1/app'
SECRET_KEY = 'kfdasferuiawohnjlkasdfjkl'
TITLE = 'monitor'
SUBTITLE = 'PyPLN cluster monitoring'
AUTHOR = u'Flávio Codeço Coelho'
AUTHOR_EMAIL = 'fccoelho@gmail.com'
KEYWORDS = 'python, PyPLN, cluster, NLP, Text processing'
DESCRIPTION = ''

# PyPLN configuration
DATABASE = 'pypln'
MANAGER_URI = "127.0.0.1:5551"
