# -*- coding:utf-8 -*-
'''
Created on 26/06/2011

@author: Flávio Codeço Coelho
'''

from setuptools import setup, find_packages


def get_requirements():
    requirements_fp = open('requirements/production.txt')
    requirements = requirements_fp.readlines()
    requirements_fp.close()
    packages = []
    for package in requirements:
        package = package.split('#')[0].strip()
        if package:
            packages.append(package)
    return packages

setup(name='pypln',
      version='0.4.0d',
      author=('Flávio Codeço Coelho <fccoelho@gmail.com>, '
              'Renato Rocha Souza <rsouza.fgv@gmail.com>, '
              'Álvaro Justen <alvarojusten@gmail.com>'),
      author_email='pypln@googlegroups.com',
      url='https://github.com/NAMD/pypln',
      description='Distributed natural language processing pipeline',
      zip_safe=False,
      entry_points={'console_scripts': ['pypln-manager = pypln.backend.manager:main',
                                        'pypln-broker = pypln.backend.broker:main',
                                        'pypln-client = pypln.backend.client:main',
                                        'pypln-pipeliner = pypln.backend.pipeliner:main',],
      },
      packages=find_packages(),
      install_requires=get_requirements(),
      test_suite='nose.collector',
      license='GPL',
)
