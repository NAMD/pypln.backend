# -*- coding:utf-8 -*-
'''
Created on 26/06/2011

@author: Flávio Codeço Coelho
'''

#from ez_setup import use_setuptools
#use_setuptools()

from setuptools import setup, find_packages


setup(name='pypln',
        version  = '0.3.1',
        author = 'Flávio Codeço Coelho',
        author_email = 'fccoelho@gmail.com',
        url = 'http://code.google.com/p/pypln/',
        description = 'Natural Language Processing Pipeline',
        zip_safe = True,
        entry_points = {
            'console_scripts': ['pypln-manager = pypln.apps.cluster.cmanager:main',
                                'slavedriver = pypln.apps.cluster.slavedriver:main',
                                'pypln-monitor = pypln.Monitors.webmonitor.monitor:main',
            ]
        },
        packages = find_packages(),
        install_requires = ["SQLAlchemy", "pyzmq", "pymongo","chardet>=1.0.1","nltk","lxml>=2.3.1","fabric","mongoengine", "psutil"],
        test_suite = 'nose.collector',
        license = 'GPL',
      )
